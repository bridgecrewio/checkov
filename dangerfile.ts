const { danger, fail, schedule, warn } = require('danger');

const IGNORE_VAR = [
  'key', 's3_key', 's3_file_key', 'local_file_path', 'self.s3_bucket', 'e', 'error', 'str(e)', 'path', 'customer_name',
  'name', 'self.framework', 'framework', 'self.graph_framework', 'file_path', 'zip_path', 'object_path',
  'definitions_context_object_path', 'root_folder', 'bucket', 'source_id', 'num_vertices',
  'num_edges', 'file_name', 'tmp_folder', 'self.bucket_name', 'repository_zip_path', 'file_size_in_mb',
  'repository_zip_path', 'event', 'block_type', 'block_name', 'graph_framework', 'custom_policies', 'checkov_check_id',
  'start_time', 'datetime.now()', 'framework.name', 'str(framework)', 'entity_id', 'full_file_path'
];

const START_END_IGNORE = [
  'path', 'len(', 'enable_', 'datetime', 'key', 'id', '_ids',
];

const LOGGING_LEVEL_PY = [
  'logging.warning', 'logging.debug', 'logging.info', 'logging.error', 'logging.warn', 'logger.info',
  'logger.warning', 'logger.debug', 'logger.error', 'logger.warn', 'self.logger.info',
  'self.logger.warning', 'self.logger.debug', 'self.logger.error', 'self.logger.warn',
];

const FIND_LOGGING_LEVEL_PY = new RegExp(`(?:${LOGGING_LEVEL_PY.join('|')})`, 'g');
const VAR_IN_LOG = '\\{([^}]*)\\}';
const VAR_IN_FUNC = '\\((.*?)\\)';
const PY_MASK_STR = 'extra={"mask": True}'
const FIND_CODE_INSIDE_BRACES_OR_AFTER_COMMA = /^.*\{[^}]*code[^}]*\}.*|.*,.*code.*/;
const FSTRING_PATTERN = /f(["'])(.*?{.*?}.*?)(\1)/;
const SUPPORTED_EXTENSIONS = ['.py'];
const EXCLUDED_FILES = ['__init__.py', 'dangerfile.ts'];
const IGNORE_COMMENT = '# danger:ignore'

function varMayContainData(varString) {
  if (IGNORE_VAR.includes(varString)) return false;
  if (START_END_IGNORE.some((ignore) => varString.trim().startsWith(ignore) || varString.trim().endsWith(ignore))) return false;
  if (varString.includes('json.dump')) {
    const varInDump = varString.match(/\((.*?)\)/)?.[1];
    if (varInDump && IGNORE_VAR.includes(varInDump)) {
      return false;
    }
  }
  return true;
}

async function failIfLoggingLineContainsSensitiveData() {
  const dangerousFiles = [];
  const changedFiles = danger.git.modified_files.concat(danger.git.created_files);
  const shouldProcessFile = (filePath) => {
    const fileExtension = filePath.substring(filePath.lastIndexOf('.'));
    if (SUPPORTED_EXTENSIONS.includes(fileExtension)) {
      const fileName = filePath.substring(filePath.lastIndexOf('/') + 1);
      if (!EXCLUDED_FILES.includes(fileName)) return true;
    }
    return false;
  };

  const processFile = async (filePath) => {
    if (!shouldProcessFile(filePath)) return;
    try {
      const fileDiff = await danger.git.diffForFile(filePath);
      const addedLinesLength = fileDiff.added.split('\n');
      const removedLinesLength = fileDiff.removed.split('\n');
      const allLines = [...addedLinesLength, ...removedLinesLength];
      for (let line of allLines) {
        if (FIND_LOGGING_LEVEL_PY.test(line) && FSTRING_PATTERN.test(line) && !line.includes(PY_MASK_STR) && !line.includes(IGNORE_COMMENT)) {
          if (FIND_CODE_INSIDE_BRACES_OR_AFTER_COMMA.test(line)) {
            const varsInLog = line.match(VAR_IN_LOG) || line.match(VAR_IN_FUNC)?.[1].split(',').slice(1) || [];
            for (const varString of varsInLog) {
              if (varMayContainData(varString)) {
                dangerousFiles.push(`file path:${filePath}, line: ${line}`);
                break;
              }
            }
          }
        }
      }
    } catch (e) {
      console.error(`Error reading file: ${filePath}, Error message: ${e}`);
    }
  };
  await Promise.all(changedFiles.map(async (filePath) => processFile(filePath)));
  if (dangerousFiles.length > 0) {
    const failureMessage = 'Logging lines with sensitive data detected, please review the following files:';
    const fileList = dangerousFiles.join('\n');
    fail(`${failureMessage}\n${fileList}`);
  }
}

schedule(failIfLoggingLineContainsSensitiveData);

async function alertPublicInterfaces() {
    let changedFiles: string[] = danger.git.modified_files || [];

    for (const changedFile of changedFiles) {
        if (changedFile.endsWith("report_types.py")) {
            warn("You've changed `report_types.py` file, that contains the contract for checkov input and output. Make sure to stay backwards compatible.")
        }
        if (changedFile.endsWith("report.py")) {
            warn("You've changed `report.py` file, that contains the contract for checkov input and output. Make sure to stay backwards compatible.")
        }
    }
}

schedule(alertPublicInterfaces)
