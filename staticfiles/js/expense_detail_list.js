document.addEventListener('DOMContentLoaded', function () {
    window.onload = function () {

        if (window.name != "any") {
            location.reload();
            window.name = "any";
        } else {
            window.name = "";
        }
    
    }
});