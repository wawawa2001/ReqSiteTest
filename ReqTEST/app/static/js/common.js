function get_cart_count(){
    count = 0
    fetch("/get_cart")
        .then(response => response.json())
        .then(data =>{
            console.log(data)
            document.getElementById("cart_count").textContent = data.cartcnt
        })
}

get_cart_count()