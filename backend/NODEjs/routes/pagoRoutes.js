const express = require('express');
const router = express.Router();
const controller = require('../controllers/pagoController');

router.get('/', controller.obtenerpago);
router.get('/:id', controller.obtenerPagoPorId);
router.post('/subasta', controller.crearPagoPendienteSubasta);
router.post('/', controller.crearPago);
router.put('/:id/anular', controller.anularPago);

module.exports = router;