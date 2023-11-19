const getOptionChart = async () => {
   try {
      const response = await fetch("/ecommerce/get_respuesta/");
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