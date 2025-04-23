from checkov.terraform.graph_builder.variable_rendering.safe_eval_functions import evaluate




input_str = 'try("local.foo.boop", "{}")'
result = evaluate(input_str)
result2 = evaluate(input_str)