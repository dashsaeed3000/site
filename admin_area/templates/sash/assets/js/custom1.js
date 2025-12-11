// section menu active
function onScroll(event) {
    const sections = document.querySelectorAll(".nav-link1");
    const scrollPos =
        window.pageYOffset ||
        document.documentElement.scrollTop ||
        document.body.scrollTop;

        sections.forEach((elem)=> {
        const val = elem.getAttribute("href");
        const refElement = document.querySelector(val);
        const scrollTopMinus = scrollPos + 50;
        if (
            refElement?.offsetTop <= scrollTopMinus &&
            refElement?.offsetTop + refElement?.offsetHeight > scrollTopMinus
        ) {
            elem.classList.add("active");
        } else {
            elem.classList.remove("active");
        }
    })
}
window.document.addEventListener("scroll", onScroll);


// FOOTER
document.getElementById("year").innerHTML = new Date().getFullYear();
