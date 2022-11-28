from flask import Flask, request, jsonify
from os import remove, getenv
import logging
import json
import subprocess
import yaml
from datetime import datetime
import re

webhook = Flask(__name__)

webhook.logger.setLevel(logging.INFO)


@webhook.route('/', methods=['GET'])
def hello():
    return "<h1 style='color:blue'>Ready!</h1>"


@webhook.route('/validate', methods=['POST'])
def validating_webhook():
    request_info = request.get_json()
    uid = request_info["request"].get("uid")

    checkovconfig = "config/.checkov.yaml"
    configfile = "config/k8s.properties"

    whorfconfig = getConfig(configfile)

    # Process config variables
    # a list of namespaces to ignore requests from
    ignore_list = whorfconfig['ignores-namespaces']

    # Check/Sanitise UID to make sure it's a k8s request and only a k8s request as it is used for filenaming
    # UUID pattern match regex
    pattern = r'\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b'
    if re.match(pattern, uid):
        webhook.logger.error("Valid UID Found, continuing")
    else:
        response = 'Invalid UID. Aborting validation'
        webhook.logger.error('K8s UID failed security checks. Request rejected!')
        return admission_response(False, uid, response)

    # check we're not in the kube-system namespace
    namespace = request_info["request"].get("namespace")
    if namespace in ignore_list:
        response = 'Namespace in ignore list. Ignoring validation'
        webhook.logger.error('Namespace in ignore list. Ignoring validation!')
        return admission_response(True, uid, response)

    jsonfile = "tmp/" + uid + "-req.json"
    yamlfile = "tmp/" + uid + "-req.yaml"

    ff = open(jsonfile, 'w+')
    yf = open(yamlfile, 'w+')
    json.dump(request_info, ff)
    yaml.dump(todict(request_info["request"]["object"]), yf)

    print("Running checkov")
    cp = subprocess.run(
        ["checkov", "--config-file", checkovconfig, "-f", yamlfile],
        universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    checkovresults = json.loads(cp.stdout)

    # check the debug env.  If 'yes' we don't delete the evidence of the scan.  Just in case it's misbehaving.
    # to active add an env DEBUG:yes to the deployment manifest
    if (getenv("DEBUG")) is not None:
        debug = getenv("DEBUG")
        if (debug.lower() != "yes"):
            remove(jsonfile)
            remove(yamlfile)

    obj_kind_name = (
        f'{request_info["request"]["object"]["kind"]}/'
        f'{request_info["request"]["object"]["metadata"]["name"]}'
    )

    if cp.returncode != 0:

        # open configfile to check for hard fail CKVs
        with open(checkovconfig, 'r') as config:
            cf = yaml.safe_load(config)

        response = ""
        if "hard-fail-on" in cf:
            hard_fails = {}
            try:
                for ckv in cf["hard-fail-on"]:
                    for fail in checkovresults["results"]["failed_checks"]:
                        if (ckv == fail["check_id"]):
                            hard_fails[ckv] = f"\n  Description: {fail['check_name']}"
                            if fail['guideline'] != "":
                                hard_fails[ckv] += f"\n  Guidance: {fail['guideline']}"

            finally:

                webhook.logger.error("hard fail error")
        
            if (len(hard_fails) > 0):
                response = f"\nCheckov found {len(hard_fails)} issues in violation of admission policy.\n"

                for ckv in hard_fails:
                    response = response + f"{ckv}:{hard_fails[ckv]}\n"

        response = response + f"Checkov found {checkovresults['summary']['failed']} total issues in this manifest.\n"
        response = response + f"\nFor complete details: {checkovresults['url']}\n"

        webhook.logger.error(f'Object {obj_kind_name} failed security checks. Request rejected!')
        return admission_response(False, uid, response)

    else:
        webhook.logger.info(f'Object {obj_kind_name} passed security checks. Allowing the request.')
        admission_resp_msg = (
            f'Checkov found {checkovresults["summary"]["failed"]} issues. None in violation of admission policy. '
            f'{checkovresults["summary"]["failed"]} issues in this manifest!'
        )
        return admission_response(True, uid, admission_resp_msg)


def todict(obj):
    if hasattr(obj, 'attribute_map'):
        result = {}
        for k, v in obj.attribute_map.items():
            val = getattr(obj, k)
            if val is not None:
                result[v] = todict(val)
        return result
    elif type(obj) == list:
        return [todict(x) for x in obj]
    elif type(obj) == datetime:
        return str(obj)
    else:
        return obj


def admission_response(allowed, uid, message):
    return jsonify({"apiVersion": "admission.k8s.io/v1",
                    "kind": "AdmissionReview",
                    "response": {
                        "allowed": allowed,
                        "uid": uid,
                        "status": {
                            "code": 403,
                            "message": message
                        }
                    }
                    })


def getConfig(configfile):
    cf = {}
    with open(configfile) as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            cf[name.strip()] = list(var.strip().split(','))
    return cf


if __name__ == '__main__':
    webhook.run(host='0.0.0.0', port=1701)
