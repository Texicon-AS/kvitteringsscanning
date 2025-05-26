#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position,bad-indentation,pointless-string-statement,superfluous-parens,line-too-long,consider-using-f-string,singleton-comparison, broad-exception-caught
"""
@file
@brief provide comamnd-line utliiteis
@remarks aux logics used to train the NLP model
"""
import os
import datetime
import subprocess
from typing import Optional
from typeguard import typechecked

@typechecked
def applyCmd(cmd : str) -> bool:
  """
  @brief performs the given bash command, and handle exceptions
  """
  try:
    result = subprocess.check_output(
      #arr_cmdToCall,
      cmd,
      stderr=subprocess.STDOUT, shell=True, timeout=None, # 60*10*10,
      universal_newlines=True)
  except subprocess.CalledProcessError as exc:
    print("!!\t [tut] operation failed")
    print("-\t reproduce: run: \"{}\"\t({})".format(cmd, __file__))
    print("-\tRaw Error Details : FAIL", exc.returncode, exc.output)
    return False
  print("Output from \"{}\": \n{}\n".format(cmd, result))
  print("\t OK: the \"{}\" worked.".format(cmd))
  return True


@typechecked
def getNewFileNameWithDateTimeAnnotation(prefix : str, isA_folderName : bool = False) -> str:
  """
  @brief get a psaudo-uniue path, using the preifx + the current date-time stamp
  @remarks if the alst char (in the prefix agument) is an os.sep direoty symbol, then it is chopped off (being prelacef by teh "_" symbol)
  """
  assert(isinstance(prefix, str))
  lastChar = prefix[len(prefix)-1]
  if(lastChar == os.sep): #! then update the string
    prefix_new = prefix[0 : len(prefix)-1]
    prefix_new += "_" #! ie, tmeov it, as we asusem ti was then not indended ... otherise, anems easiely beocmes odd
    prefix = prefix_new
    #! Note: the below assignment is worong, as een from [https://stackoverflow.com/questions/10631473/str-object-does-not-support-item-assignment]
    # prefix[len(prefix)-1] = "_" #! ie, tmeov it, as we asusem ti was then not indended ... otherise, anems easiely beocmes odd
  suffix = ".csv"
  if(isA_folderName):
    suffix = ""
  fileNameResult = "{}_{}{}".format(prefix, datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p"), suffix)
  return fileNameResult

@typechecked
def moveFile(fileName_old : str, fileName_new : str) -> bool:
  """
  @brief move fileName_old to fileName_new
  @return True if no erorr was thrown
  """
  assert(fileName_new != fileName_old)
  if(os.path.exists(fileName_old) == False):
    print("!!\t[commandLine.py]\t Unable to move file=\"{}\" (did not exists!) to new location=\"{}\"".format(fileName_old, fileName_new))
    return False
  try:
    print("(info)\t[commandLine.py]\t rename \"{}\" into \"{}\"".format(fileName_old, fileName_new))
    os.rename(fileName_old, fileName_new) #! eg, to aovid ovewriting the preivosu modle (when a new run is appleid=called=started)
    return True
  except Exception as _:
    print("!!\t[commandLine.py]\t Unable to move file=\"{}\" to new location=\"{}\"".format(fileName_old, fileName_new))
    return False

@typechecked
def moveFileToDateTimeAnnotationIfAlreadyExists(fileName : str, isA_folderName : Optional[bool] = False) -> bool:
  """ @brief move file to a pasuo-unique path if the file alreayd exiists """
  if(os.path.exists(fileName)):
    isA_folderName = os.path.isdir(fileName) #! used to configure the file-name
    fileName_new = getNewFileNameWithDateTimeAnnotation(fileName, isA_folderName = isA_folderName)
    print(f"(info)\t[CommandLine.py]\t move \"{fileName}\" to a newLocation({fileName_new})")
    return moveFile(fileName, fileName_new)
  return True #! as the oepraionw as a scuess


@typechecked
def main() -> None:
  """
  @brief baisc eval
  """
  moveFileToDateTimeAnnotationIfAlreadyExists("model-best-dummy/")


#! *************************************************************************************************************
if __name__ == "__main__" :
  main()
