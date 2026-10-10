const db = require('../config/db');

function montoACentavos(monto) {
  const [unidades, decimales = ''] = String(monto).split('.');
  return Number(unidades) * 100 + Number(decimales.padEnd(2, '0'));
}

class FacturaModel {
  static async obtenerTodas() {
    const [rows] = await db.query('SELECT * FROM pago');
    return rows;
  }

  static async obtenerPorId(id) {
    const [rows] = await db.query('SELECT * FROM pago WHERE id_pago = ?', [id]);
    return rows[0];
  }

  static async obtenerCompradorPorCorreo(correo) {
    const [rows] = await db.query(
      `SELECT id_usuario
       FROM usuario
       WHERE correo = ? AND rol = 'comprador' AND activo = 1`,
      [correo]
    );
    return rows[0]?.id_usuario;
  }

  static async crear(monto, estado_pago, fechapago, subasta_id_subasta, usuario_id_comprador, metodo = 'transferencia') {
    const [result] = await db.query(
      'INSERT INTO pago (monto, estado_pago, fechapago, subasta_id_subasta, usuario_id_comprador, metodo) VALUES (?, ?, ?, ?, ?, ?)',
      [monto, estado_pago, fechapago, subasta_id_subasta, usuario_id_comprador, metodo]
    );
    return result.insertId;
  }

  static async crearPendienteDeSubasta(monto, subasta_id_subasta, usuario_id_comprador) {
    const connection = await db.getConnection();
    let transaccionIniciada = false;

    try {
      await connection.beginTransaction();
      transaccionIniciada = true;

      const [pagosExistentes] = await connection.execute(
        `SELECT id_pago, metodo, monto, estado_pago, subasta_id_subasta, usuario_id_comprador
         FROM pago
         WHERE subasta_id_subasta = ?
         FOR UPDATE`,
        [subasta_id_subasta]
      );

      if (pagosExistentes.length > 0) {
        const pagoExistente = pagosExistentes[0];
        if (
          pagoExistente.metodo !== 'transferencia'
          || montoACentavos(pagoExistente.monto) !== montoACentavos(monto)
          || pagoExistente.usuario_id_comprador !== usuario_id_comprador
        ) {
          const error = new Error('El pago existente no coincide con el ganador actual');
          error.code = 'PAYMENT_CONFLICT';
          throw error;
        }

        await connection.commit();
        transaccionIniciada = false;
        return { ...pagoExistente, creado: false };
      }

      const [resultado] = await connection.execute(
        `INSERT INTO pago (
           metodo, monto, estado_pago, fechapago, subasta_id_subasta, usuario_id_comprador
         )
         VALUES ('transferencia', ?, 'en_espera', NULL, ?, ?)`,
        [monto, subasta_id_subasta, usuario_id_comprador]
      );
      await connection.commit();
      transaccionIniciada = false;

      return {
        id_pago: resultado.insertId,
        metodo: 'transferencia',
        monto,
        estado_pago: 'en_espera',
        subasta_id_subasta,
        usuario_id_comprador,
        creado: true
      };
    } catch (error) {
      if (transaccionIniciada) {
        await connection.rollback();
      }
      if (error.code === 'ER_DUP_ENTRY') {
        const [pagosExistentes] = await connection.execute(
          `SELECT id_pago, metodo, monto, estado_pago, subasta_id_subasta, usuario_id_comprador
           FROM pago
           WHERE subasta_id_subasta = ?`,
          [subasta_id_subasta]
        );
        if (pagosExistentes.length > 0) {
          const pagoExistente = pagosExistentes[0];
          if (
            pagoExistente.metodo === 'transferencia'
            && montoACentavos(pagoExistente.monto) === montoACentavos(monto)
            && pagoExistente.usuario_id_comprador === usuario_id_comprador
          ) {
            return { ...pagoExistente, creado: false };
          }
        }
      }
      throw error;
    } finally {
      connection.release();
    }
  }

  static async anular(id) {
    const [result] = await db.query(
      'UPDATE pago SET estado_pago = "rechazado" WHERE id_pago = ?',
      [id]
    );
    return result.affectedRows > 0;
  }
}

module.exports = FacturaModel;
