var job_menu = []
let li = document.getElementsByClassName("job-menu__item")
// 获取主类目
for (let i = 0; i < li.length; i++) {
    let tmp = {}
    if (li[i].getElementsByClassName("job-menu__sub__title").length <= 0) {
        break
    }
    tmp["title"] = li[i].getElementsByClassName("job-menu__sub__title")[0].textContent
    //获取标题
    let job_list = li[i].getElementsByClassName("job-menu__sub__list")
    tmp["items"] = []
    for (let j = 0; j < job_list.length; j++) {
        for (let k = 0; k < job_list[j].children.length; k++) {
            let tmp2 = {}
            tmp2["name"] = job_list[j].children[k].textContent
            tmp2["url"] = job_list[j].children[k].href
            tmp["items"].push(tmp2)
        }
    }
    job_menu.push(tmp)
}
console.log(job_menu)
