let shipping = document.getElementById("shipping");
let finalPrice = document.getElementById("final_price");

let basePrice = {{ total_price }};

shipping.addEventListener("change", function(){
    let shipCost = parseInt(this.value);

    let total = basePrice + shipCost;

    finalePrice.innerHtml = "₹" + total;
})