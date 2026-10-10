const express = require('express');
const router = express.Router();
const controller = require('../controllers/transferenciaController');

router.get('/', controller.obtenerTransferencias);
router.get('/:id', controller.obtenerTransferenciaPorId);
router.post('/', controller.crearTransferencia);
router.put('/:id/anular', controller.anularTransferencia);

module.exports = router;