// tu-script.js
var lastScrollTop = 0;

window.addEventListener("scroll", function() {
  var st = window.pageYOffset || document.documentElement.scrollTop;
  var header = document.querySelector('header');

  if (st > lastScrollTop) {
    // Desplazamiento hacia abajo, oculta el encabezado
    header.classList.add('oculto');
  } else {
    // Desplazamiento hacia arriba, muestra el encabezado
    header.classList.remove('oculto');
  }

  lastScrollTop = st;
});
