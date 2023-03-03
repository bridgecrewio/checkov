const access_key =  "AKIAIOSFODNN7EXAMPLE"
const secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
function compact(arr: string[]) {
  if (arr.length > 10)
    return arr.slice(0, 10)
  return arr
}