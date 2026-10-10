#pragma once
#include <array>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <sys/socket.h>
#include <unistd.h>

// Cooperating endpoints only. The caller transfers an authenticated descriptor.
// No listener, cross-app access, or automatic game attachment.
namespace um {
struct Event {
    uint32_t epoch, sequence, tick, entity, generation;
    int32_t x_milli, y_milli, value;
    uint32_t kind; // 1=spawn, 2=position, 3=damage, 4=pause, 5=resume
};
enum class Result { ok, empty, full, disconnected, invalid, stale, paused };
class Endpoint {
    int fd_;
    uint32_t epoch_, tx_=0, rx_=0;
    bool paused_=false;
    static void put(unsigned char* p, uint32_t v) {
        for(int i=0;i<4;++i) p[i]=static_cast<unsigned char>(v>>(8*i));
    }
    static uint32_t get(const unsigned char* p) {
        uint32_t v=0; for(int i=0;i<4;++i) v|=uint32_t(p[i])<<(8*i); return v;
    }
public:
    // Ownership of a SOCK_SEQPACKET descriptor passes to Endpoint.
    Endpoint(int fd,uint32_t epoch):fd_(fd),epoch_(epoch) {
        int type=0; socklen_t n=sizeof(type);
        if(fd<0 || !epoch || getsockopt(fd,SOL_SOCKET,SO_TYPE,&type,&n) || type!=SOCK_SEQPACKET) {
            if(fd>=0) close(fd);
            throw std::invalid_argument("epoch and SOCK_SEQPACKET descriptor required");
        }
    }
    Endpoint(const Endpoint&)=delete;
    Endpoint& operator=(const Endpoint&)=delete;
    ~Endpoint(){close(fd_);}
    Result send(Event e) {
        if(e.kind<1 || e.kind>5) return Result::invalid;
        if(tx_==UINT32_MAX) return Result::stale; // establish a new session
        unsigned char b[48]{};
        put(b,0x31464d55); put(b+4,1); put(b+8,epoch_); put(b+12,tx_+1);
        put(b+16,e.tick); put(b+20,e.entity); put(b+24,e.generation);
        put(b+28,uint32_t(e.x_milli)); put(b+32,uint32_t(e.y_milli));
        put(b+36,uint32_t(e.value)); put(b+40,e.kind);
        ssize_t n=::send(fd_,b,sizeof(b),MSG_DONTWAIT|MSG_NOSIGNAL);
        if(n<0 && (errno==EAGAIN || errno==EWOULDBLOCK || errno==EINTR)) return Result::full;
        if(n!=sizeof(b)) return Result::disconnected;
        ++tx_; return Result::ok;
    }
    Result receive(Event& out) {
        unsigned char b[49]{};
        ssize_t n=recv(fd_,b,sizeof(b),MSG_DONTWAIT);
        if(n<0 && (errno==EAGAIN || errno==EWOULDBLOCK || errno==EINTR)) return Result::empty;
        if(n<=0) return Result::disconnected;
        if(n!=48 || get(b)!=0x31464d55 || get(b+4)!=1 || get(b+44)!=0) return Result::invalid;
        if(get(b+8)!=epoch_ || get(b+12)<=rx_) return Result::stale;
        uint32_t k=get(b+40); if(k<1 || k>5) return Result::invalid;
        rx_=get(b+12);
        if(k==4) paused_=true;
        else if(k==5) paused_=false;
        else if(paused_) return Result::paused;
        // Preserve signed bit patterns without implementation-defined casts.
        auto signed32=[](uint32_t v){int32_t s; std::memcpy(&s,&v,4); return s;};
        out={epoch_,rx_,get(b+16),get(b+20),get(b+24),signed32(get(b+28)),
             signed32(get(b+32)),signed32(get(b+36)),k};
        return Result::ok;
    }
};
}
