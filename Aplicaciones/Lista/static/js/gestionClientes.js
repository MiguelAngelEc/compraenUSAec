// Envia una Alerta de estar seguro de eliminar un cliente
const btnEliminacion=document.querySelectorAll(".btnEliminacion");

(function(){
    btnEliminacion.forEach(btn=>{
        btn.addEventListener('click',(e)=>{
            const confirmacion=confirm('Seguro de eliminar Cliente?');
            if(!confirmacion){
                e.preventDefault();
            }
        })
    })
})();

// Agregar la clase 'show' a la alerta para mostrarla
document.addEventListener('DOMContentLoaded', function() {
    let alerta = document.getElementById('my-alert');
    alerta.classList.add('show');
});

// Remover la clase 'show' después de 5 segundos
setTimeout(function() {
    let alerta = document.getElementById('my-alert');
    alerta.classList.remove('show');
}, 2000);

// Codigo de ingresar datgos al recibo
let idFila = 1;
function agregarFila() {
    // Obtener el número de filas actual
    let numeroFilas = document.getElementById('tabla-recibos').getElementsByTagName('tr').length;

    // Obtener los valores de los campos input
    let miCampoNumerico = document.getElementById('miCampoNumerico').value;
    let tienda = document.getElementById('tienda-input').value;
    let wr = document.getElementById('wr-input').value;
    let tracking = document.getElementById('tracking-input').value;
    let precio = document.getElementById('precio-input').value;
    let precio_l = document.getElementById('precio_l-input').value;
    


    // Calcular el resultado de la multiplicación
    let valor_peso = miCampoNumerico * precio_l;

     // Calcular el resultado de sumar
     let precioNum = isNaN(precio) ? 0 : Number(precio);
     let valorPesoNum = isNaN(valor_peso) ? 0 : Number(valor_peso);
     let total_recibo = isNaN(precioNum) || isNaN(valorPesoNum) ? 0 : precioNum + valorPesoNum;
    

     
    // Crear una nueva fila en la tabla con los valores ingresados
    let nuevaFila = '<tr>' +
      '<td id="tienda-' + (numeroFilas + 1) + '">' + tienda + '</td>' +
      '<td id="wr-' + (numeroFilas + 1) + '">' + wr + '</td>' +
      '<td id="tracking-' + (numeroFilas + 1) + '">' + tracking + '</td>' +
      '<td id="precio-' + (numeroFilas + 1) + '">' + precio + '</td>' +
      '<td id="precio_l-' + (numeroFilas + 1) + '">' + precio_l + '</td>' +
      '<td id="valor_peso-' + (numeroFilas + 1) + '">' + valor_peso + '</td>' +
      '<td id="total_recibo' + (numeroFilas + 1) + '">' + total_recibo + '</td>' +
      '</tr>';
    
    // Agregar la nueva fila a la tabla
    document.getElementById('tabla-recibos').insertAdjacentHTML('beforeend', nuevaFila);

     // Incrementar el contador de la fila
     idFila++;

    // Limpiar los campos input
    document.getElementById('tienda-input').value = '';
    document.getElementById('wr-input').value = '';
    document.getElementById('tracking-input').value = '';
    document.getElementById('precio-input').value = '';
    document.getElementById('precio_l-input').value = '';
    document.getElementById('valor_peso-' + idFila).textContent = '';
    document.getElementById('total_recibo-' + idFila).textContent = '';
  }

// Suma total
function sumarCampos() {
  const camposSuma = document.querySelectorAll('#tabla-recibos td[id^="total_recibo"]');
  let total = 0;
  for (let i = 0; i < camposSuma.length; i++) {
    const valorCampo = parseFloat(camposSuma[i].textContent);
    console.log(`Valor obtenido del campo ${i}: ${valorCampo}`);
    if (!isNaN(valorCampo)) {
      total += valorCampo;
    }
  }
  document.getElementById('resultado').textContent = total.toFixed(2);
}
document.addEventListener('DOMContentLoaded', sumarCampos);

// Calcular el resultado Total

function calcular() {
    let valor_peso2 = (document.getElementById('total_recibo').value);
    let abono = parseFloat(document.getElementById('txtAbono').value);
    let flete = parseFloat(document.getElementById('txtFlete').value);
    let isd = parseFloat(document.getElementById('txtISD').value);
  
    if (isNaN(valor_peso2) || isNaN(abono) || isNaN(flete) || isNaN(isd)) {
      document.getElementById('resultado_td').textContent = "Por favor, ingrese valores numéricos en todos los campos";
    } else {
      let resultado = (valor_peso2 - abono) + flete + isd;
      document.getElementById('resultado_td').textContent = resultado;
    }

    document.getElementById('txtAbono').value = '';
    document.getElementById('txtFlete').value = '';
    document.getElementById('txtISD').value = '';
  }



  // Obtenemos el campo numérico
  const campoNumerico = document.getElementById("miCampoNumerico");

  // Asignamos un listener para el evento "change"
  campoNumerico.addEventListener("change", () => {
    // Guardamos el valor del campo numérico en el almacenamiento local
    localStorage.setItem("miCampoNumerico", campoNumerico.value);
  });
  
  // Asignamos un listener para el evento "load" del objeto "window"
  window.addEventListener("load", () => {
    // Obtenemos el valor del campo numérico desde el almacenamiento local
    const valorCampoNumerico = localStorage.getItem("miCampoNumerico");
  
    // Si el valor existe, lo asignamos al campo numérico
    if (valorCampoNumerico) {
      campoNumerico.value = valorCampoNumerico;
    }
  });

