const FacturaModel = require('../models/pagoModels');

exports.obtenerpago = async (req, res) => {
  try {
    const pago = await FacturaModel.obtenerTodas();
    res.json(pago);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.obtenerPagoPorId = async (req, res) => {
  try {
    const pago = await FacturaModel.obtenerPorId(req.params.id);
    if (!pago) return res.status(404).json({ mensaje: 'Pago no encontrado' });
    res.json(pago);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
exports.crearPago = async (req, res) => {
  const {
    monto,
    estado_pago,
    fechapago,
    fecha_pago,
    subasta_id_subasta,
    usuario_id_comprador,
    metodo = 'transferencia'
  } = req.body;
  const fechaPago = fechapago ?? fecha_pago ?? null;
  if (!['efectivo', 'transferencia'].includes(metodo)) {
    return res.status(400).json({
      status: 'error',
      error: 'El método debe ser efectivo o transferencia'
    });
  }

  try {
    const id = await FacturaModel.crear(monto, estado_pago, fechaPago, subasta_id_subasta, usuario_id_comprador, metodo);
    res.status(201).json({ id, monto, estado_pago, fechapago: fechaPago, subasta_id_subasta, usuario_id_comprador, metodo });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.crearPagoPendienteSubasta = async (req, res) => {
  const { monto, subasta_id_subasta, correo } = req.body || {};
  const idSubasta = Number(subasta_id_subasta);
  const montoTexto = String(monto);

  if (
    !Number.isSafeInteger(idSubasta) || idSubasta < 1
    || typeof correo !== 'string'
    || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)
    || !/^(?:0|[1-9]\d{0,7})(?:\.\d{1,2})?$/.test(montoTexto)
    || Number(montoTexto) <= 0
  ) {
    return res.status(400).json({
      status: 'error',
      error: 'Se requieren un ID de subasta positivo, un correo válido y un monto positivo válido'
    });
  }

  try {
    const idComprador = await FacturaModel.obtenerCompradorPorCorreo(correo.trim());
    if (!idComprador) {
      return res.status(404).json({
        status: 'error',
        error: 'No existe un comprador activo con ese correo'
      });
    }

    const pago = await FacturaModel.crearPendienteDeSubasta(
      montoTexto,
      idSubasta,
      idComprador
    );
    res.status(pago.creado ? 201 : 200).json({ status: 'success', ...pago });
  } catch (err) {
    console.error('No se pudo crear el pago pendiente de la subasta:', err);
    if (err.code === 'PAYMENT_CONFLICT') {
      return res.status(409).json({ status: 'error', error: err.message });
    }
    res.status(500).json({
      status: 'error',
      error: 'No se pudo crear el pago pendiente de la subasta'
    });
  }
};

exports.anularPago = async (req, res) => {
  try {
    const anulada = await FacturaModel.anular(req.params.id);
    if (!anulada) return res.status(404).json({ mensaje: 'Pago no encontrado' });
    res.json({ mensaje: 'Pago anulado con éxito' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};