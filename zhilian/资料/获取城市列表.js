let citylist = window.__INITIAL_STATE__
let old_list = citylist["cityList"].cityMapList
let new_list = {}

for (let key in old_list) {
    new_list[key] = []
    for (var i in old_list[key]) {
        let tmp = {}
        let data = old_list[key][i]
        tmp['name'] = old_list[key][i]["name"]
        tmp['code'] = old_list[key][i]["code"]
        tmp['login'] = old_list[key][i]["url"].includes("searchresult.ashx") ? true : false
        new_list[key].push(tmp)
    }
}
console.log(new_list)
