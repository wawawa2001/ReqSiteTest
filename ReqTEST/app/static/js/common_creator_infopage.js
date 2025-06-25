
function backlocation() {
    const currentPath = window.location.pathname;
    const newPath = currentPath.substring(0, currentPath.lastIndexOf('/'));
    return newPath || '/';
}

function get_creatorID(){
    const path = window.location.pathname;
    const id = path.split('/')[2];
    return id
}

function setting_icon_position(){
    usericon = document.getElementById("usericon")
    userheader = document.getElementById("userheader")

    userheaderRect = userheader.getBoundingClientRect();
    userheaderLeft = userheaderRect.left;

    usericon.style.left = (userheaderLeft + 100) + "px";
}

function follow(){
    creator_id = get_creatorID()
    fetch("/follow", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(creator_id)
        })
        .then(response => response.json())
        .then(data => {
            if(data.msg != ""){
                alert(data.msg)
            }

            change_follow_status(data.is_follow)

            document.getElementById("follower").innerText = data.follower
        })
        .catch(error => console.error('Error:', error))
}

function change_follow_status(flg){
    if(flg){
        elem = document.getElementById("followbtn")
        elem.style.backgroundColor = "#1BB299"
        elem = document.getElementById("followbtn_text")
        elem.style.color = "white"
        elem.innerText = "フォロー中"
    }else{
        elem = document.getElementById("followbtn")
        elem.style.backgroundColor = "white"
        elem = document.getElementById("followbtn_text")
        elem.style.color = "black"
        elem.innerText = "フォローする"
    }
}

function init_func() {
    setting_icon_position();
    judge_follow()
}

document.addEventListener("DOMContentLoaded", ()=>{
    init_func();
})