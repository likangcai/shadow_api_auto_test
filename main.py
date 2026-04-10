from config.config import config
from runner.runner import runner
from common.log import log

if __name__ == "__main__":
    log.info("Starting API automated test framework")
    test_runner = config.get('test_runner', 'pytest')
    
    if test_runner == 'unittest':
        result = runner.run_with_unittest()
    else:
        result = runner.run_with_pytest()
    
    log.info("Test execution completed")
