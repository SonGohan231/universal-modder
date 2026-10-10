#include "bridge.hpp"
#include <cassert>
#include <cstdio>
#include <sys/wait.h>
using namespace um;
int main(){
 int f[2]; assert(socketpair(AF_UNIX,SOCK_SEQPACKET,0,f)==0);
 pid_t child=fork(); assert(child>=0);
 if(child==0){
  close(f[0]); Endpoint guest(f[1],7); Event e{};
  for(int i=0;i<1000;++i){
   auto r=guest.receive(e);
   if(r==Result::empty){usleep(1000);continue;}
   assert(r==Result::ok && e.entity==42 && e.x_milli==-250 && e.kind==1);
   e.kind=3; e.value=10; assert(guest.send(e)==Result::ok); _exit(0);
  } _exit(2);
 }
 close(f[1]); Endpoint host(f[0],7);
 Event e{0,0,123,42,1,-250,500,100,1}; assert(host.send(e)==Result::ok);
 bool received=false;
 for(int i=0;i<1000;++i){auto r=host.receive(e); if(r==Result::empty){usleep(1000);continue;}
  assert(r==Result::ok && e.kind==3 && e.value==10); received=true;break;}
 assert(received);int status; assert(waitpid(child,&status,0)==child && WIFEXITED(status) && WEXITSTATUS(status)==0);
 int p[2];assert(socketpair(AF_UNIX,SOCK_SEQPACKET,0,p)==0);
 Endpoint a(p[0],8),b(p[1],8);
 e.kind=4;assert(a.send(e)==Result::ok); assert(b.receive(e)==Result::ok);
 e.kind=2;assert(a.send(e)==Result::ok);assert(b.receive(e)==Result::paused);
 e.kind=5;assert(a.send(e)==Result::ok);assert(b.receive(e)==Result::ok);
 e.kind=2;assert(a.send(e)==Result::ok);assert(b.receive(e)==Result::ok);
 unsigned char bad[60]{};assert(::send(p[0],bad,sizeof(bad),0)==sizeof(bad));assert(b.receive(e)==Result::invalid);
 int q[2];assert(socketpair(AF_UNIX,SOCK_SEQPACKET,0,q)==0);
 Endpoint old(q[0],1),fresh(q[1],2);assert(old.send(e)==Result::ok);assert(fresh.receive(e)==Result::stale);
 int count=0;while(a.send(e)==Result::ok){assert(++count<100000);}
 assert(count>0);
 puts("PASS: separate-process roundtrip, signed coordinates, pause/resume, malformed packet, stale epoch, backpressure");
}
