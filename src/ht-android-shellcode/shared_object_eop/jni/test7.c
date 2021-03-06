#include <stdio.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <linux/user.h>
#include <sys/syscall.h>
#include <string.h>
#include <stdlib.h>

#define SYSCOUNT 100
#define OFF1 0x1e0
#define OFF2 0x111cd4


int main(int argc, char ** argv) {
  int status;
  pid_t child;
  int i = 0;
  char cmd[64];
  char *vold_bin = "/system/bin/vold";
  char *dump_file = "dumped_mem";
  int syscount = 0;
  FILE *file = NULL;
  char heap[9];
  char stack[9];
  long val, val2;
  int child_argv_start;

  child = fork();
  if(child == 0) {
    child_argv_start = 1;
    ptrace(PTRACE_TRACEME, 0, NULL, NULL);
    execl(vold_bin, vold_bin);
  }
  else {
    memset(cmd, 0, sizeof(cmd));
    snprintf(cmd, sizeof(cmd), "cat /proc/%d/maps > %s", child, dump_file);
    wait(&status);
    if(WIFEXITED(status)) 
      _exit (WEXITSTATUS(status));

    ptrace(PTRACE_SYSCALL, child, NULL, NULL);
    wait(&status);
    while (1) {
      i++;
      if(i == SYSCOUNT) {
	printf("Going to sleep");
	sleep(20);
	//system(cmd);
	break;
      }
    
    if(WIFEXITED(status))
      break;
    
    ptrace(PTRACE_SYSCALL, child, NULL, NULL);
    wait(&status);
    }
  }



  return 0;


}

