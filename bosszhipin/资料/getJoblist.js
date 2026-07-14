var text = ""
let dom = document.getElementsByClassName("menu-sub")
for (let i=0;i<dom.length;i++){
    //主干分类标题
    text +=dom[i].getElementsByTagName("p")[0].textContent +"\n"
    for(let k=0;k<dom[i].getElementsByTagName("ul")[0].children.length;k++){
        // 子干分类标题
        text +="\t"+dom[i].getElementsByTagName("ul")[0].children[k].getElementsByTagName("h4")[0].innerText+"\n"
        for(let j=0;j<dom[i].getElementsByTagName("ul")[0].children[k].getElementsByTagName("a").length;j++){
            text +="\t\t" + dom[i].getElementsByTagName("ul")[0].children[k].getElementsByTagName("a")[j].innerText+"\n"
        }
    }
}

console.log(text)