#WARNING: in case this wasn't obvious, this is an example thrift file and should not be 
#consumed by anything in production.  
include "wizecommerce.exception.invalid.thrift"
include "wizecommerce.bizobj.example.thrift"
include "wizecommerce.enum.change.thrift"

namespace java com.wizecommerce.service.example
namespace rb ExampleClient


##See wizecommerce.services.example.thrift for more info, same idea.
const string VERSION = "0.0.1"
#Optional
const string GROUPID = "com.wizecommerce.data"

# define the types here.
typedef wizecommerce.bizobj.example.Example Example
typedef wizecommerce.enum.change.Change Change

#
# Tag Service API
#

service ExampleService  {

/**
   I know this rare, but this is an example of documentation.  You should replace this text will relevant information about yourservice.


   @param id.	 	        : id identifying the object being requested.
   @param apiKey            : the key to uniquely identify the requestor so that service author can apply proper QoS
                              parameters.
   @return Example          : we will return the complete Example object if we find the tag matching the given id. If none is
                             matching we will be sending an empty Example object with "empty" flag set to true.
*/


Example getExampleById(1:required i64 id, 2:required string apiKey)
               throws (1:wizecommerce.exception.invalid.InvalidRequestException ire),

/**
  Enables the utilizations multi-get capabilities in underlying object store implementations.
  Our current caches, memcached and cassandra, has in-built multi-get support enabling us to retrieve multiple objects
  at the same time.

  @param exampleIds     : set of example ids to be retrieved
  @param apiKey         : the key to uniquely identify the requestor so that service author can apply proper QoS
                          parameters.
*/

map<i64, Example> getExampleByIds(1:required set<i64> exampleIds,
                                                               2:required string apiKey)
                                                               throws (1:wizecommerce.exception.invalid.InvalidRequestException ire)


Change getStatus(1:required i64 id, 2:required string apiKey)
                                                               throws (1:wizecommerce.exception.invalid.InvalidRequestException ire)

}
