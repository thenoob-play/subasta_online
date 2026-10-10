const express = require('express');
const path = require('node:path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

// Rutas corregidas apuntando a la carpeta /routers/
const pagoRoutes = require('./routes/pagoRoutes');
const transferenciaRoutes = require('./routes/transferenciaRoutes');
// const detalleVentasRoutes = require('./routers/detalleVentasRoutes');

const app = express();
app.use(express.json());

// Montaje de rutas
app.use('/api/pagos', pagoRoutes);
app.use('/api/transferencias', transferenciaRoutes);
//app.use('/api/detalle-ventas', detalleVentasRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`API Gateway corriendo en http://localhost:${PORT}`);
});


// npm init -y
// npm install express mysql2 dotenv
// npm install express mysql2 dotenv
// Bash
// npm install -D nodemon
