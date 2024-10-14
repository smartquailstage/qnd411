    // Función para abrir una pestaña
    function openTab(evt, tabId) {
        var i, tabContent, tabButtons;
  
        // Ocultar todos los contenidos de las pestañas
        tabContent = document.getElementsByClassName("tab-content");
        for (i = 0; i < tabContent.length; i++) {
          tabContent[i].style.display = "none";
        }
  
        // Desactivar todos los botones de las pestañas
        tabButtons = document.getElementsByClassName("tab-button");
        for (i = 0; i < tabButtons.length; i++) {
          tabButtons[i].className = tabButtons[i].className.replace(" active", "");
        }
  
        // Mostrar el contenido de la pestaña seleccionada y activar el botón
        document.getElementById(tabId).style.display = "block";
        evt.currentTarget.className += " active";
      }
  
      // Función para actualizar el gráfico
      function updateGrafico() {
        var timestamp = new Date().getTime();
        document.getElementById('ventas-grafico').src = "{% url 'ventas_grafico' %}?v=" + timestamp;
        document.getElementById('ventas-grafico-2').src = "{% url 'ventas_grafico' %}?v=" + timestamp;
      }
  
      // Actualizar el gráfico cada 5 minutos
      setInterval(updateGrafico, 300000); // 300000 ms = 5 minutos
  
      // Actualizar el gráfico al cargar la página
      document.addEventListener('DOMContentLoaded', updateGrafico);
  
      // Abrir la primera pestaña por defecto
      document.addEventListener('DOMContentLoaded', function() {
        document.querySelector(".tab-button").click();
      });
  
  
      document.querySelector('form').addEventListener('submit', function(event) {
              event.preventDefault();
              const periodo = document.querySelector('select[name="periodo"]').value;
              const img = document.getElementById('chart');
              img.src = `{% url 'ventas_grafico' %}?periodo=${periodo}&t=${new Date().getTime()}`;
          });
  