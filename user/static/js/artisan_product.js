
document.addEventListener("DOMContentLoaded", function () {

    const category = document.getElementById("category");
    const productType = document.getElementById("productType");

    category.addEventListener("change", function () {

        let selectedCategory = this.value;

        for (let option of productType.options) {

            if (option.value === "") continue;

            if (option.getAttribute("data-category") === selectedCategory) {
                option.style.display = "block";
            } else {
                option.style.display = "none";
            }
        }

        productType.value = "";
    });
});
</script>