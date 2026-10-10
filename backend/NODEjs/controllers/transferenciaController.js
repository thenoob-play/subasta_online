const TransferenciaModel = require('../models/transferenciaModels');

const METODOS_PAGO = new Set(['nequi', 'bancolombia', 'mercadopago']);
const TIPOS_DOCUMENTO = new Set(['CC', 'TI', 'CE', 'PAS', 'NIT', 'PEP', 'PPT']);

function parsearId(value) {
  if (!/^[1-9]\d*$/.test(value)) {
    return null;
  }
  const id = Number(value);
  return Number.isSafeInteger(id) ? id : null;
}

function textoValido(value, maxLength) {
  return typeof value === 'string'
    && value.trim().length > 0
    && value.trim().length <= maxLength;
}

function enviarError(res, error) {
  if (error.code === 'PAYMENT_NOT_FOUND') {
    return res.status(404).json({ status: 'error', error: error.message });
  }
  if (error.code === 'PAYMENT_NOT_PENDING'
    || error.code === 'PAYMENT_METHOD_MISMATCH'
    || error.code === 'TRANSFER_ALREADY_EXISTS'
    || error.code === 'TRANSFER_ALREADY_VOIDED') {
    return res.status(409).json({ status: 'error', error: error.message });
  }
  if (error.code === 'ER_DUP_ENTRY') {
    return res.status(409).json({
      status: 'error',
      error: 'El código de verificación ya está registrado'
    });
  }

  console.error('Error en el servicio de transferencias:', error);
  return res.status(500).json({
    status: 'error',
    error: 'No se pudo completar la operación de transferencia'
  });
}

exports.obtenerTransferencias = async (req, res) => {
  try {
    const transferencias = await TransferenciaModel.obtenerTodas();
    return res.json({ status: 'success', data: transferencias });
  } catch (error) {
    return enviarError(res, error);
  }
};

exports.obtenerTransferenciaPorId = async (req, res) => {
  const id = parsearId(req.params.id);
  if (id === null) {
    return res.status(400).json({ status: 'error', error: 'ID de transferencia inválido' });
  }

  try {
    const transferencia = await TransferenciaModel.obtenerPorId(id);
    if (!transferencia) {
      return res.status(404).json({ status: 'error', error: 'Transferencia no encontrada' });
    }
    return res.json({ status: 'success', data: transferencia });
  } catch (error) {
    return enviarError(res, error);
  }
};

exports.crearTransferencia = async (req, res) => {
  const datos = req.body;
  const pagoId = datos && parsearId(String(datos.pago_id_pago));

  if (
    !datos
    || Array.isArray(datos)
    || !METODOS_PAGO.has(datos.metodo_pago)
    || !textoValido(datos.codigo_verificacion, 45)
    || !textoValido(datos.nombre_asociado, 100)
    || !textoValido(datos.numero_cuenta, 45)
    || !textoValido(datos.numero_identificacion, 45)
    || !TIPOS_DOCUMENTO.has(datos.tipo_documento)
    || pagoId === null
  ) {
    return res.status(400).json({
      status: 'error',
      error: 'Datos inválidos: revisa método, código, datos del titular, documento e ID de pago'
    });
  }

  try {
    const id = await TransferenciaModel.crear({
      metodo_pago: datos.metodo_pago,
      codigo_verificacion: datos.codigo_verificacion.trim(),
      nombre_asociado: datos.nombre_asociado.trim(),
      numero_cuenta: datos.numero_cuenta.trim(),
      numero_identificacion: datos.numero_identificacion.trim(),
      tipo_documento: datos.tipo_documento,
      pago_id_pago: pagoId
    });
    const transferencia = await TransferenciaModel.obtenerPorId(id);
    return res.status(201).json({ status: 'success', data: transferencia });
  } catch (error) {
    return enviarError(res, error);
  }
};

exports.anularTransferencia = async (req, res) => {
  const id = parsearId(req.params.id);
  if (id === null) {
    return res.status(400).json({ status: 'error', error: 'ID de transferencia inválido' });
  }

  try {
    await TransferenciaModel.anular(id);
    const transferencia = await TransferenciaModel.obtenerPorId(id);
    return res.json({
      status: 'success',
      mensaje: 'Transferencia anulada; el pago quedó rechazado',
      data: transferencia
    });
  } catch (error) {
    if (error.code === 'TRANSFER_NOT_FOUND') {
      return res.status(404).json({ status: 'error', error: error.message });
    }
    return enviarError(res, error);
  }
};
