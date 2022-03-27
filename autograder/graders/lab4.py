from itertools import permutations

def grade_solution(student_output, solution):
  grades = {}

  for field in student_output:
    grades[field] = {'match': False, 'expected': '', 'obtained': ''}

    if student_output[field]['match'] == 'any':
      # This will essentially be every test
      grades[field]['match'] = len(student_output[field]['value']) > 0
      # If any output is generated
      if not grades[field]['match']:
        grades[field]['obtained'] = student_output[field]['value'] if field in student_output else ''

    else:
      print(f"Obtained unexpected match value: {solution[field]['match']}")

  return grades

def generate_expected_output(subtask_info):
  return ''

def parse_output(output, task=None, correct_output=False):
  # Correct output will always be false here
  output_lines = output.split('\n')
  task_output = {}
  field_match = {
    "Train output": 'any',
    "Test output": 'any'
  }

  for line in output_lines:
    if not line.strip(): continue

    line = line.lower()

    if line.startswith("[train error"):
      curr_field = "Train output"
      if curr_field not in task_output:
        task_output[curr_field] = {'value': []}

      task_output[curr_field]['match'] = field_match[curr_field] # Always any
      err_str = line.strip().split()[-1]
      try:
        err = float(err_str)
      except ValueError:
        # Don't append --> value will be empty
        continue

      task_output[curr_field]['value'].append(err) # Append output for each 2k iters

    elif line.startswith("[test error]"):
      curr_field = "Test output"

      if curr_field not in task_output:
        task_output[curr_field] = {'value': []}

      task_output[curr_field]['match'] = field_match[curr_field] # Always any
      err_str = line.strip().split()[-1]
      try:
        err = float(err_str)
      except ValueError:
        # Don't append --> value will be empty
        continue

      task_output[curr_field]['value'].append(err) # Append output for each 2k iters



  return task_output

def log_results(log_file, report, verbose=True):
  log_file.write(f"{report['id']}\n")
  log_file.write("================\n\n")

  # errors with archive and folder structure
  log_file.write("=== UNARCHIVE AND STRUCTURE ===\n")
  if not report['unarchive']:
    log_file.write(f"Failed! Error: {report['error']}\n\n")
    return
  else:
    log_file.write("OK!\n\n")

  # errors with compiling
  log_file.write("=== COMPILE ===\n")
  if not report['compile']:
    log_file.write(f"Failed! Error: {report['error']}\n\n")
    return
  elif report['lang'] == 'python':
    log_file.write("Skipping (python)\n\n")
  else:
    log_file.write("OK!\n\n")
  
  # evaluation results
  log_file.write('=== EVALUATION ===\n')


  total_tests, total_passed = 0, 0
  for subtask in report['evaluation_results']:
    test_instances = report['evaluation_results'][subtask]
    subtask_tests = len(test_instances)
    passed_tests = sum(i['test_passed'] for i in test_instances)
    total_tests += subtask_tests
    total_passed += passed_tests
  log_file.write("\n=== TOTAL RESULTS ===\n")
  log_file.write(f"{total_passed} / {total_tests} tests passed. ({total_passed * 100. / total_tests:.2f}%)\n")

  #log_file.write(str(report))
  for subtask in sorted(report['evaluation_results'], reverse=False): 
    log_file.write(f"\n== {subtask.upper()} ==\n")
    
    if verbose:  # logged in a separate file for each student with detailed info about failed tests
      test_instances = report['evaluation_results'][subtask]
      for i in test_instances:
        if not i['test_passed']:
          log_file.write(f"\n- Failed test: {i['command']}\n")
          if not i['execute']:
            log_file.write(f"Execution failed with error (process returned non-zero exit code):\n{i['output']}\n")
          elif not i['timeout']:
            log_file.write("Execution timed out.\n")
        else:
          log_file.write(f"{i['command']}\n")
          log_file.write("--> Complete obtained output:\n")
          log_file.write(i['output'] + '\n')
