// =====================================================================
// CONSULTA DE POWER QUERY: Analisis_Ventas   (tabla de hechos)
// ---------------------------------------------------------------------
// Qué hace: importa el CSV de ventas, convierte los tipos de dato y aplica
//           las dos decisiones de limpieza del proyecto.
//
// Nota: la ruta del archivo (C:\RUTA\...) debe apuntar a la carpeta datos/
//       de donde se descargue el repositorio.
//
// LAS TRES DECISIONES QUE CONTIENE
//   1. Precio y Total se convierten APARTE y con configuración regional
//      "en-US". El texto "$124.43" usa punto decimal; si Power BI lo lee con
//      la configuración de un equipo en español de España, el punto es un
//      separador de miles y el precio pasa a 12,443 (importes x100).
//   2. Fecha NO se convierte con "en-US": "01-05-2018" es día-mes-año
//      (1 de mayo). Con en-US se leería 5 de enero y se dañarían todas las
//      series de tiempo y el churn.
//   3. IVA: el archivo trae 21 % (España); el modelo usa 15 % (Ecuador).
//      Por eso la columna Total del archivo NO debe usarse: está calculada
//      con 21 % y ya no coincide con [ventas_totales].
// =====================================================================
let
    // --- 1. Origen ---------------------------------------------------
    Origen = Csv.Document(
        File.Contents("C:\RUTA\datos\ventas_tecnologia_barcelona.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    #"Encabezados promovidos" = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),

    // --- 2. Tipos de dato (SIN Precio ni Total, se quedan como texto) --
    #"Tipo cambiado" = Table.TransformColumnTypes(
        #"Encabezados promovidos",
        {
            {"Agencia", type text}, {"Vendedor", type text}, {"Cliente", type text},
            {"Ciudad", type text}, {"tipocliente", type text}, {"DNI", type text},
            {"Factura", type text}, {"Fecha", type date}, {"Cantidad", Int64.Type},
            {"Descuento", Percentage.Type}, {"Iva", Percentage.Type},
            {"codigocategoria", type text}, {"categorianombre", type text},
            {"marcanombre", type text}, {"codigoarticulo", type text},
            {"descripcionarticulo", type text}
        }
    ),

    // --- 3. Precio y Total con configuración regional en-US ----------
    #"Moneda en-US" = Table.TransformColumnTypes(
        #"Tipo cambiado",
        {{"Precio", Currency.Type}, {"Total", Currency.Type}},
        "en-US"
    ),

    // --- 4. IVA del modelo: 21 % (archivo) -> 15 % (Ecuador) ---------
    #"IVA 15 %" = Table.ReplaceValue(
        #"Moneda en-US", 0.21, 0.15, Replacer.ReplaceValue, {"Iva"}
    ),

    // --- 5. Limpieza de agencias: 'Tech DCM Barcelona' era la misma
    //        agencia Norte con otro nombre (el modelo solo tiene 3) ----
    #"Agencia corregida" = Table.ReplaceValue(
        #"IVA 15 %", "Tech DCM Barcelona", "Tech BCN Norte", Replacer.ReplaceText, {"Agencia"}
    )
in
    #"Agencia corregida"

// ---------------------------------------------------------------------
// COMPROBACIÓN después de Cerrar y aplicar (sin filtros):
//   [ventas_netas]   = 1,811,167.84
//   [iva_usd]        =   271,675.18
//   [ventas_totales] = 2,082,843.02
// Si ves 208 millones o 219 millones, hay un problema de configuración
// regional en Precio. Si ves 2.19 millones, el IVA sigue en 21 %.
// ---------------------------------------------------------------------
