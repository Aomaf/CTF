
import shutil
import sqlite3
import threading
import os.path
import threading
import os
import json
import sys
import fileinput
from sys import platform
import datetime
import subprocess
from subprocess import PIPE
import pymysql

def printit():
    threading.Timer(5, printit).start() # number is seconds
    try:
        mydb = pymysql.connect(host = "localhost", database = "qupcljvd_qupc_win_main_db", user = "qupcljvd_qupc_main_db_user", password = "m=XksrFS{tab", port = 3306)
        query = mydb.cursor()
        statement = """ SELECT * FROM home_submission WHERE status = %s """
        values = (0)
        query.execute(statement,values)
        submit = query.fetchone()
        
        if submit == None or len(submit) <= 0: return
        else:
            ''' obtain key variables related to the submission, we don't use (SELECT *) to avoid changes in the order
            of elements in the DB in case of migrations. Therefore, we fetch with the query what values are needed by name'''
            submission_id = str(submit[0])
            statement = """ SELECT challenge_id, contestant_id, filepath, language, level, result, counter, view_date, solve_date FROM home_submission WHERE id = %s """
            values = (submission_id)
            query.execute(statement,values)
            submit = query.fetchone()
            challenge_id = str(submit[0])
            contestant_id = str(submit[1])
            filePathSolve = str(submit[2])
            language = str(submit[3])
            level = str(submit[4])
            oldResult = submit[5]
            counter = submit[6]
            view_date = str(submit[7])
            solve_date = str(submit[8])

            if submission_id == None or challenge_id == None or contestant_id == None or filePathSolve == None or view_date == None or solve_date == None:
                raise TypeError("Missing submission data. Contact QuPC team for help.")
            
            # directory of the submission
            pathDis:str = str(filePathSolve)
            end = pathDis.rindex(os.sep)
            pathDis = pathDis[0:end]
            
            # obtain key variables related to the challenge
            statement = """ SELECT filepath, filepathPy, filepathCpp, belongsToEvent_id FROM home_challenge WHERE id = %s """
            values = (challenge_id)
            query.execute(statement, values)
            challenge = query.fetchone()
            filePathMainJava = str(challenge[0])
            filePathMainPy = str(challenge[1])
            filePathMainCpp = str(challenge[2])
            belongsToEvent = challenge[3]
            
            if filePathMainJava == None and filePathMainPy == None and filePathMainCpp == None:
                raise OSError("Unable to locate the main execution files. Contact QuPC team for help")
            
            if oldResult>=100:
                statement = """ UPDATE home_submission SET status = %s WHERE id = %s """
                values = (1, submission_id)
                query.execute(statement, values)
                mydb.commit()
                mydb.close()
                return # contestant already has the top mark for this challenge
            
            if not os.path.exists(filePathSolve): raise TypeError("Unable to load submitted code. Contact QuPC team")
            
            if (submit) and (str(language) == 'Java'):
                
                if not filePathSolve.endswith(".java"): raise TypeError("Unsupported Java code has been submitted. Try again.")         
                if not os.path.exists(filePathMainJava): raise TypeError("Unable to load main execution file. Contact QuPC team")
                
                for i, line in enumerate(fileinput.input(str(filePathMainJava), inplace=1)):
                                sys.stdout.write(line.replace('package', '//'))
                                if i == 4: sys.stdout.write('\n')
                for i, line in enumerate(fileinput.input(str(filePathSolve), inplace=1)):
                                sys.stdout.write(line.replace('package', '//'))
                                if i == 4: sys.stdout.write('\n')
                pathMainClass = pathDis+' Main'
                
                cmd = cmd2 = None
                
                if(platform == 'win32' or platform == 'cygwin'):
                    cmd= "javac -cp json-simple-1.1.1.jar;. "+str(filePathMainJava)+" "+str(filePathSolve)+" -d "+str(pathDis)+""
                    cmd2= "java -cp json-simple-1.1.1.jar;" + str(pathMainClass) +" -Xms10m -Xmx100m"
                elif(platform == 'linux' or platform == 'darwin'):
                    cmd= "javac -cp json-simple-1.1.1.jar:. "+str(filePathMainJava)+" "+str(filePathSolve)+" -d "+str(pathDis)+""
                    cmd2= "java -cp json-simple-1.1.1.jar:" + str(pathMainClass) +" -Xms10m -Xmx100m"
                else: raise OSError("Operating system is not supported. Please contact QuPC team for help.")
                
                compileProcess = None
                #try: compileProcess = subprocess.run( cmd1, shell=True, capture_output=True, text=True, universal_newlines=True) # only applicable for python >= 3.7
                try: compileProcess = subprocess.run( cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
                except Exception as e: raise OSError("Unable to compiler the submitted code: unknown error: %s", e)
                
                if compileProcess != None and compileProcess.returncode != 0: raise OSError(str(compileProcess.stderr))

                executeProcess = None
                #try: executeProcess = subprocess.run( cmd2, shell=True, capture_output=True, text=True, universal_newlines=True, timeout=20) # only applicable for python >= 3.7
                try: executeProcess = subprocess.run( cmd2, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True, timeout=20)
                except Exception as e: raise OSError("Unable to execute successfully the submitted code: execution has exceeded the timeout.")
                
                if executeProcess != None and executeProcess.returncode != 0: raise OSError(str(executeProcess.stderr))
                
            elif (submit) and (str(language) == 'Python'):
                if not filePathSolve.endswith(".py"): raise TypeError("Unsupported Python source code has been submitted. Try again.")
                if not os.path.exists(filePathMainPy): raise TypeError("Unable to load the main execution file. Contact QuPC team")
                
                compileProcess = None
                try:
                    cmd = "cp " + filePathMainPy + " " + pathDis + " "  
                    #compileProcess = subprocess.run( cmd, shell=True, capture_output=True, text=True, universal_newlines=True) # only applicable for python >= 3.7
                    compileProcess = subprocess.run( cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
                except Exception as e: raise OSError("Unable to copy necessary files to your user directory. Contact QuPC team.")
                if compileProcess != None and compileProcess.returncode != 0: raise OSError(str(compileProcess.stderr))
                
                executeProcess = None
                try:
                    cmd = "python3 " + pathDis + os.sep + "Main.py "
                    #executeProcess = subprocess.run( cmd, shell=True, capture_output=True, text=True, universal_newlines=True, timeout=20) # only applicable for python >= 3.7
                    executeProcess = subprocess.run( cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True, timeout=20)
                except Exception as e: raise OSError("Unable to execute successfully the submitted code: execution has exceeded the timeout.")
                if executeProcess != None and executeProcess.returncode != 0: raise OSError(str(executeProcess.stderr))
                
            elif (submit) and (str(language) == 'Cpp'): return
            else: raise OSError("Unable to determine the language of the submitted code.")
                
            p_dir = sys.path[0]
            p_dir_xu = 0
            jsonName = None
                
            # go through the directory of submission and search for json file
            for top_dir, dir_list, obj_list in os.walk(p_dir):
                if p_dir_xu == 0:
                    p_dir_xu = p_dir_xu + 1
                    for obj in obj_list:
                        if obj.endswith('.json'):
                            jsonName = obj
                            break

            if jsonName == None: raise OSError("Unable to locate Json file of your solution. Contact the QuPC team for help")
            
            jsonPath:str = ""+ pathDis + os.sep + jsonName
            shutil.move(jsonName, jsonPath)
            file = open(jsonPath)
            data = json.load(file)
            passed_outputs = 0
            total_outputs = 0
            json_string:str=""
            
            total_outputs = len(data)
            for i in range(0, total_outputs, 1):
                entry = data['Test ' + str(i+1)]
                json_string += 'Test ' + str(i+1) + ":"
                for key in entry:
                    json_string+="\n"
                    if isinstance(entry[key], list) == True:
                        json_string += "\t" + str(key) +" => "
                        for e in entry[key]: json_string += ' ' + str(e)
                    else: json_string += "\t" + str(key) +" => "+ str(entry[key])
                json_string+="\n"
                if(entry['Status'] == 'PASSED'): passed_outputs = passed_outputs + 1
                
            result:float = (float(passed_outputs) / float(total_outputs)) * 100
            file.close()
            
            countsub = int(counter) + 1
            
            # multiple submission affects total rating
            sumresult = float(float(result) - (2 * (countsub - 1)))
                    
            # obtain the difference between the view date and submission date for
            # sorting contestant
            solve_date = solve_date[:-7]
            view_date = view_date[:-7]
                                
            tS = datetime.datetime.strptime(solve_date, '%Y-%m-%d %H:%M:%S') # submission time
            tV = datetime.datetime.strptime(view_date,  '%Y-%m-%d %H:%M:%S') # view time
            diff = tS - tV # ts always greater than tv
            
            diff2 = str(diff.total_seconds())
                    
            # commit a major update for this submission
            query = mydb.cursor()
            statement = """ UPDATE home_submission SET status = %s, counter = %s , diff = %s, result = %s, json_text = %s, sum_result = %s, note = %s WHERE id = %s """
            values = (1, str(countsub) ,str(diff2), str(result), json_string, str(sumresult), None,submission_id)
            query.execute(statement, values)
            mydb.commit()
                
            if not belongsToEvent:
                query = mydb.cursor()
                statement = """ SELECT MAX(sum_result) FROM home_submission WHERE contestant_id = %s  and level = %s """
                values = (contestant_id, level)
                query.execute(statement, values)
                rated_result = query.fetchone()
                
                if int(rated_result[0]): sumresult = float(rated_result[0])
                    
                if   str(level) == 'Level 1': statement = """ UPDATE home_contestant SET user_scoreL1 = %s WHERE id = %s """
                elif str(level) == 'Level 2': statement = """ UPDATE home_contestant SET user_scoreL2 = %s WHERE id = %s """
                elif str(level) == 'Level 3': statement = """ UPDATE home_contestant SET user_scoreL3 = %s WHERE id = %s """
                elif str(level) == 'Level 4': statement = """ UPDATE home_contestant SET user_scoreL4 = %s WHERE id = %s """
                elif str(level) == 'Level 5': statement = """ UPDATE home_contestant SET user_scoreL5 = %s WHERE id = %s """
                values = (sumresult, contestant_id)
                query.execute(statement, values)
                mydb.commit()
            # end if belong
        # end of valid submission received
    # end of try
    except (TypeError, OSError) as e:
        errStat = """ UPDATE home_submission SET status = %s, note = %s WHERE id = %s"""
        values = (3, str(e), submission_id)
        query = mydb.cursor()
        query.execute(errStat, values)
        mydb.commit()
        print("TypeError or OSError: " +str(e))
    except Exception as e:
        errStat = """UPDATE home_submission SET status = %s, note = %s WHERE id = %s"""
        statement = "Unknown error. Please contact QuPC team for help."
        values = (3, statement, submission_id)
        query = mydb.cursor()
        query.execute(errStat, values)
        mydb.commit()
        print("Exception: " +str(e))
    finally:
        if mydb.open == True: mydb.close()
    
printit()