namespace java com.wizecommerce.service.common
namespace rb InvalidException

const string VERSION = "0.0.1"

/** Invalid request could mean a parameter is malformed.
    why contains an associated error message.
*/
exception InvalidRequestException {
    1: required string why
}
