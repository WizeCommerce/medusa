#WARNING: in case this wasn't obvious, this is an example thrift file and should not be 
#consumed by anything in production.  

namespace java com.wizecommerce.service.common
namespace rb ExampleBizobj

## When developing use 0.0.0 when you wish to make a release, 
#bump the version.
#
#If this is an existing object, then simply ignore the version until you're ready.
const string VERSION = "0.0.1" 
const string GROUPID = "com.wizecommerce.data" #optional will default to assigned value.


struct Example {
   #Make your objects primary key required.
   1: required i64 id,
   ## Make any fields that might be null optional
   2: optional string name, 
   ## ALWAYS include this field if you plan on serializing the object 
   58: optional bool empty,
}
