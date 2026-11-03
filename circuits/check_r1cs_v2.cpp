// Independent streaming standard-R1CS/WTNS checker. Uses OpenSSL only when
// a linear combination contains a non-Boolean field value or coefficient.
#include <openssl/bn.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <array>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Byte=unsigned char;
uint32_t u32(const Byte* p){uint32_t v;std::memcpy(&v,p,4);return v;}
uint64_t u64(const Byte* p){uint64_t v;std::memcpy(&v,p,8);return v;}
void require(bool b,const char* msg){if(!b)throw std::runtime_error(msg);}
struct Map{
 int fd;size_t size;const Byte* p;
 explicit Map(const char* name){fd=open(name,O_RDONLY);require(fd>=0,"OPEN_FAILED");struct stat st{};require(fstat(fd,&st)==0,"STAT_FAILED");size=st.st_size;p=(Byte*)mmap(nullptr,size,PROT_READ,MAP_PRIVATE,fd,0);require(p!=MAP_FAILED,"MMAP_FAILED");}
 ~Map(){munmap((void*)p,size);close(fd);}
};
struct Section{const Byte* p=nullptr;uint64_t size=0;};
std::array<Section,4> sections(const Map& f,const char* magic){
 require(f.size>=12&&!std::memcmp(f.p,magic,4),"BAD_MAGIC");uint32_t n=u32(f.p+8);const Byte* p=f.p+12;
 std::array<Section,4>s{};
 for(uint32_t i=0;i<n;i++){require(p+12<=f.p+f.size,"TRUNCATED_SECTION");uint32_t type=u32(p);uint64_t len=u64(p+4);p+=12;require(len<=uint64_t(f.p+f.size-p),"BAD_SECTION_SIZE");if(type<4){require(!s[type].p,"DUPLICATE_SECTION");s[type]={p,len};}p+=len;}
 require(p==f.p+f.size,"TRAILING_BYTES");return s;
}

struct Value{bool small=true;__int128 n=0;BIGNUM* big=nullptr;};
struct Checker{
 const Byte* witness;uint32_t nw;BIGNUM* prime=nullptr;BN_CTX* ctx=nullptr;
 std::array<std::array<Byte,32>,17> negatives{};
 uint64_t big_constraints=0,checked=0;
 Checker(const Byte* w,uint32_t n,const Byte* field):witness(w),nw(n){
  prime=BN_lebin2bn(field,32,nullptr);ctx=BN_CTX_new();require(prime&&ctx,"BN_INIT_FAILED");
  for(int i=1;i<=16;i++){BIGNUM* t=BN_dup(prime);require(t&&BN_sub_word(t,i),"BN_SUB_FAILED");BN_bn2lebinpad(t,negatives[i].data(),32);BN_free(t);}
 }
 ~Checker(){BN_free(prime);BN_CTX_free(ctx);}
 bool small_coefficient(const Byte* p,int64_t& value){
  static const Byte zero[24]={};
  uint64_t a=u64(p);
  if(a<=1000000 && !std::memcmp(p+8,zero,24)){value=a;return true;}
  // Fast paths cover all Boolean Keccak-kernel coefficients.
  for(int i=1;i<=4;i++)if(!std::memcmp(p,negatives[i].data(),32)){value=-i;return true;}
  return false;
 }
 BIGNUM* to_bn(Value& v){
  if(!v.small)return v.big;
  BIGNUM* out=BN_CTX_get(ctx);require(out,"BN_ALLOC_FAILED");
  unsigned __int128 a=v.n<0?-v.n:v.n;Byte bytes[16];
  for(int i=0;i<16;i++){bytes[i]=a&255;a>>=8;}
  require(BN_lebin2bn(bytes,16,out),"BN_SMALL_FAILED");if(v.n<0)BN_set_negative(out,1);return out;
 }
 Value lc(const Byte*& p,const Byte* end){
  require(p+4<=end,"TRUNCATED_LC");uint32_t count=u32(p);p+=4;require(uint64_t(end-p)>=uint64_t(count)*36,"TRUNCATED_TERMS");
  Value result;std::vector<uint32_t> large_seen;std::array<uint32_t,16> seen{};
  if(count>16)large_seen.reserve(count);
  for(uint32_t j=0;j<count;j++,p+=36){
   uint32_t wire=u32(p);require(wire<nw,"WIRE_OUT_OF_BOUNDS");
   // Object-map readers overwrite duplicates, so reject them as malformed.
   if(count<=16){for(uint32_t k=0;k<j;k++)require(seen[k]!=wire,"DUPLICATE_WIRE_IN_LC");seen[j]=wire;}
   else large_seen.push_back(wire);
   const Byte* value=witness+uint64_t(wire)*32;static const Byte zeros[32]={};
   if(!std::memcmp(value,zeros,32))continue;
   int64_t coefficient=0;bool cs=small_coefficient(p+4,coefficient);
   bool one=value[0]==1&&!std::memcmp(value+1,zeros,31);
   if(result.small&&one&&cs){result.n+=coefficient;continue;}
   if(result.small){result.big=to_bn(result);result.small=false;}
   BIGNUM* a=BN_CTX_get(ctx);BIGNUM* b=BN_CTX_get(ctx);BIGNUM* term=BN_CTX_get(ctx);require(a&&b&&term,"BN_ALLOC_FAILED");
   require(BN_lebin2bn(p+4,32,a)&&BN_lebin2bn(value,32,b),"BN_PARSE_FAILED");
   require(BN_mod_mul(term,a,b,prime,ctx)&&BN_mod_add(result.big,result.big,term,prime,ctx),"BN_EVAL_FAILED");
  }
  if(count>16){std::sort(large_seen.begin(),large_seen.end());for(size_t j=1;j<large_seen.size();j++)require(large_seen[j]!=large_seen[j-1],"DUPLICATE_WIRE_IN_LC");}
  return result;
 }
 bool constraint(const Byte*& p,const Byte* end){
  BN_CTX_start(ctx);Value a=lc(p,end),b=lc(p,end),c=lc(p,end);bool good;
  if(a.small&&b.small&&c.small){__int128 product;bool overflow=__builtin_mul_overflow(a.n,b.n,&product);if(!overflow){good=product==c.n;BN_CTX_end(ctx);checked++;return good;}}
  big_constraints++;
  BIGNUM* aa=to_bn(a);BIGNUM* bb=to_bn(b);BIGNUM* cc=to_bn(c);BIGNUM* product=BN_CTX_get(ctx);require(product,"BN_ALLOC_FAILED");
  require(BN_mod_mul(product,aa,bb,prime,ctx)&&BN_mod_sub(product,product,cc,prime,ctx),"BN_CONSTRAINT_FAILED");good=BN_is_zero(product);BN_CTX_end(ctx);checked++;return good;
 }
};

int main(int argc,char** argv){
 auto began=std::chrono::steady_clock::now();
 try{
  require(argc==3,"USAGE: check_r1cs circuit.r1cs witness.wtns");Map r(argv[1]),w(argv[2]);auto rs=sections(r,"r1cs"),ws=sections(w,"wtns");
  require(rs[1].size==64&&ws[1].size==40&&rs[2].p&&ws[2].p,"MISSING_STANDARD_SECTIONS");
  require(u32(rs[1].p)==32&&u32(ws[1].p)==32&&!std::memcmp(rs[1].p+4,ws[1].p+4,32),"FIELD_MISMATCH");
  uint32_t nw=u32(rs[1].p+36),n=u32(rs[1].p+60);require(nw==u32(ws[1].p+36),"WIRE_COUNT_MISMATCH");require(ws[2].size==uint64_t(nw)*32,"WITNESS_SIZE_MISMATCH");
  static const Byte zeros[31]={};require(ws[2].p[0]==1&&!std::memcmp(ws[2].p+1,zeros,31),"CONSTANT_WIRE_NOT_ONE");
  const Byte* prime_bytes=rs[1].p+4;
  for(uint32_t i=0;i<nw;i++){
   const Byte* v=ws[2].p+uint64_t(i)*32;bool less=false;
   for(int j=31;j>=0;j--){if(v[j]<prime_bytes[j]){less=true;break;}if(v[j]>prime_bytes[j])break;}
   require(less,"NONCANONICAL_WITNESS_FIELD_ELEMENT");
  }
  Checker check(ws[2].p,nw,rs[1].p+4);const Byte* p=rs[2].p;const Byte* end=p+rs[2].size;
  for(uint32_t i=0;i<n;i++){
   if(!check.constraint(p,end)){std::cout<<"{\"all_passed\":false,\"first_bad_constraint\":"<<i<<",\"checked\":"<<check.checked<<"}\n";return 1;}
   if(i&&i%5000000==0)std::cerr<<"checked "<<i<<"/"<<n<<"\n";
  }
  require(p==end,"UNREAD_CONSTRAINT_BYTES");double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count();
  std::cout<<"{\"all_passed\":true,\"constraints_checked\":"<<check.checked<<",\"wires\":"<<nw<<",\"big_field_constraints\":"<<check.big_constraints<<",\"elapsed_s\":"<<elapsed<<"}\n";return 0;
 }catch(const std::exception& e){std::cout<<"{\"all_passed\":false,\"error\":\""<<e.what()<<"\"}\n";return 2;}
}
