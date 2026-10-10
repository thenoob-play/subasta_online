const db = require('../config/db');

const TRANSFERENCIA_SELECT = `
  SELECT
    t.id_transferencia_pago,
    t.metodo_pago,
    t.codigo_verificacion,
    t.nombre_asociado,
    t.numero_cuenta,
    t.numero_identificacion,
    t.tipo_documento,
    t.pago_id_pago,
    p.estado_pago
  FROM transferencia_pago AS t
  INNER JOIN pago AS p ON p.id_pago = t.pago_id_pago
`;

function crearError(mensaje, code) {
  const error = new Error(mensaje);
  error.code = code;
  return error;
}

class TransferenciaModel {
  static async obtenerTodas() {
    const [rows] = await db.query(
      `${TRANSFERENCIA_SELECT} ORDER BY t.id_transferencia_pago DESC`
    );
    return rows;
  }

  static async obtenerPorId(id) {
    const [rows] = await db.execute(
      `${TRANSFERENCIA_SELECT} WHERE t.id_transferencia_pago = ?`,
      [id]
    );
    return rows[0] || null;
  }

  static async crear(datos) {
    const connection = await db.getConnection();
    let transaccionIniciada = false;

    try {
      await connection.beginTransaction();
      transaccionIniciada = true;

      const [pagos] = await connection.execute(
        'SELECT estado_pago, metodo FROM pago WHERE id_pago = ? FOR UPDATE',
        [datos.pago_id_pago]
      );
      if (pagos.length === 0) {
        throw crearError('Pago no encontrado', 'PAYMENT_NOT_FOUND');
      }
      if (pagos[0].estado_pago !== 'en_espera') {
        throw crearError(
          'Solo se puede registrar una transferencia para un pago en espera',
          'PAYMENT_NOT_PENDING'
        );
      }
      if (pagos[0].metodo !== 'transferencia') {
        throw crearError(
          'El método del pago no permite registrar una transferencia',
          'PAYMENT_METHOD_MISMATCH'
        );
      }

      const [transferencias] = await connection.execute(
        'SELECT id_transferencia_pago FROM transferencia_pago WHERE pago_id_pago = ? LIMIT 1',
        [datos.pago_id_pago]
      );
      if (transferencias.length > 0) {
        throw crearError(
          'El pago ya tiene una transferencia registrada',
          'TRANSFER_ALREADY_EXISTS'
        );
      }

      const [result] = await connection.execute(
        `INSERT INTO transferencia_pago (
          metodo_pago,
          codigo_verificacion,
          nombre_asociado,
          numero_cuenta,
          numero_identificacion,
          tipo_documento,
          pago_id_pago
        ) VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [
          datos.metodo_pago,
          datos.codigo_verificacion,
          datos.nombre_asociado,
          datos.numero_cuenta,
          datos.numero_identificacion,
          datos.tipo_documento,
          datos.pago_id_pago
        ]
      );

      await connection.execute(
        `UPDATE pago
         SET estado_pago = 'realizado', fechapago = CURRENT_TIMESTAMP
         WHERE id_pago = ?`,
        [datos.pago_id_pago]
      );
      await connection.commit();
      transaccionIniciada = false;

      return result.insertId;
    } catch (error) {
      if (transaccionIniciada) {
        await connection.rollback();
      }
      throw error;
    } finally {
      connection.release();
    }
  }

  static async anular(id) {
    const connection = await db.getConnection();
    let transaccionIniciada = false;

    try {
      await connection.beginTransaction();
      transaccionIniciada = true;

      const [transferencias] = await connection.execute(
        `SELECT t.pago_id_pago, p.estado_pago
         FROM transferencia_pago AS t
         INNER JOIN pago AS p ON p.id_pago = t.pago_id_pago
         WHERE t.id_transferencia_pago = ?
         FOR UPDATE`,
        [id]
      );
      if (transferencias.length === 0) {
        throw crearError('Transferencia no encontrada', 'TRANSFER_NOT_FOUND');
      }
      if (transferencias[0].estado_pago !== 'realizado') {
        throw crearError(
          'La transferencia ya fue anulada o su pago no está realizado',
          'TRANSFER_ALREADY_VOIDED'
        );
      }

      await connection.execute(
        `UPDATE pago
         SET estado_pago = 'rechazado', fechapago = NULL
         WHERE id_pago = ?`,
        [transferencias[0].pago_id_pago]
      );
      await connection.commit();
      transaccionIniciada = false;

      return true;
    } catch (error) {
      if (transaccionIniciada) {
        await connection.rollback();
      }
      throw error;
    } finally {
      connection.release();
    }
  }
}

module.exports = TransferenciaModel;
