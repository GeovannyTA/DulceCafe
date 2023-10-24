const getOptionChart = async () => {
   try {
      const response = await fetch("http://127.0.0.1:8000/ecommerce/get_respuesta/");
      return await response.json();
   } catch (error) {
      alert(error);
   }
};

const initChar = async () => {
   const myChart = echarts.init(document.getElementById("chart"));

   myChart.setOption(await getOptionChart());
   myChart.resize();
};

window.addEventListener('load', async () => {
   await initChar();
});