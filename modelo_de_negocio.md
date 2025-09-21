# Modelo de Negocio: Simulación Empresarial "Captop"

## 1. Resumen Ejecutivo

Este documento detalla el modelo de negocio del juego de simulación "Captop". El juego posiciona al jugador como el gerente general de una empresa manufacturera y comercializadora en funcionamiento en Chile. El objetivo principal es tomar decisiones estratégicas y operativas a lo largo de varios períodos para asegurar la rentabilidad, sostenibilidad y crecimiento del valor patrimonial de la compañía.

El modelo de negocio se basa en principios contables y financieros chilenos, incorporando variables macroeconómicas clave como la Unidad de Fomento (UF) y la Unidad Tributaria Mensual (UTM), las cuales son obtenidas en tiempo real desde el Banco Central de Chile. El jugador debe gestionar un ciclo de negocio completo, desde la adquisición de materias primas hasta la venta del producto final, pasando por la producción, la gestión de inventarios, la fijación de precios, las estrategias de marketing y las decisiones de financiamiento.

La empresa comienza con una situación financiera predefinida, incluyendo activos, pasivos y patrimonio, lo que obliga al jugador a gestionar una operación ya existente en lugar de comenzar desde cero. El éxito se mide a través del análisis de los estados financieros clásicos: Balance General, Estado de Resultados y Flujo de Caja.

## 2. Concepto del Negocio y Objetivos

### 2.1. Premisa Fundamental

El juego simula la gestión de una **empresa manufacturera y comercializadora de tamaño mediano, con operaciones en Chile**. La empresa no es una startup; el jugador asume el control de una compañía en marcha, con un historial financiero, activos operativos y obligaciones existentes.

El jugador actúa como el **Gerente General** y es responsable de todas las decisiones estratégicas y tácticas que afectan el rendimiento de la empresa.

### 2.2. Objetivos del Jugador

El objetivo principal del juego es **maximizar el valor para los accionistas**. Este objetivo se traduce en las siguientes metas cuantificables:

1.  **Maximizar la Rentabilidad**: Lograr el mayor resultado neto (utilidades) posible en cada período, gestionando eficientemente los ingresos y costos. El **Estado de Resultados** es el principal indicador de este objetivo.
2.  **Aumentar el Patrimonio Neto**: Incrementar el valor contable de la empresa a través de la acumulación de utilidades y una gestión financiera prudente. El **Balance General** refleja el crecimiento del patrimonio.
3.  **Asegurar la Liquidez**: Mantener suficiente efectivo (caja) para cumplir con las obligaciones a corto plazo, como el pago a proveedores, salarios e impuestos. El **Flujo de Caja** es crucial para monitorear la salud financiera.
4.  **Gestionar el Endeudamiento**: Utilizar el financiamiento de manera estratégica para apalancar el crecimiento, sin caer en un nivel de deuda insostenible que ponga en riesgo la solvencia de la empresa.

El éxito se evalúa al final de un número predeterminado de períodos (típicamente 8, según se infiere de la interfaz principal), comparando los resultados financieros finales con los iniciales.

## 3. Análisis del Balance General Inicial (Período 0)

La empresa inicia en el Período 0 con una estructura financiera ya establecida, la cual se detalla a continuación. Los valores están expresados en pesos chilenos (CLP).

### 3.1. Activos (Lo que la empresa posee)

#### 3.1.1. Activo Circulante (Activos de corto plazo, < 1 año)
*   **Deudores por Venta:** `$ 492.244.175`
    *   **Descripción:** Este es el monto que los clientes le deben a la empresa por ventas de productos ya entregados pero aún no pagados. Es una cuenta de "Cuentas por Cobrar".
    *   **Implicancia en el juego:** El jugador deberá gestionar el cobro de esta deuda para convertirla en efectivo (Caja) y financiar las operaciones.
*   **Productos Terminados:** `$ 120.207.027`
    *   **Descripción:** Valor del inventario de productos listos para la venta.
    *   **Implicancia en el juego:** Es el stock inicial disponible para generar ingresos en el primer período. Su gestión es clave para evitar quiebres de stock o sobrecostos de almacenamiento.

#### 3.1.2. Activo Fijo o No Circulante (Activos de largo plazo)
*   **Terrenos:** `$ 40.500.000`
    *   **Descripción:** Valor de los terrenos propiedad de la empresa. No se deprecian.
*   **Plantas:** `$ 750.000.000`
    *   **Descripción:** Valor de las instalaciones de producción (fábricas).
*   **Edificios de Administración y Venta:** `$ 30.000.000`
    *   **Descripción:** Oficinas y otras construcciones no productivas.
*   **Muebles, Máquinas y Otros:** `$ 12.000.000`
    *   **Descripción:** Equipamiento de oficina y maquinaria menor.
    *   **Implicancia en el juego:** Estos activos fijos (Plantas, Edificios, etc.) generarán un gasto por depreciación en cada período, afectando el Estado de Resultados.

### 3.2. Pasivos (Lo que la empresa debe)

#### 3.2.1. Pasivo Circulante (Deudas de corto plazo, < 1 año)
*   **Préstamos de Corto Plazo:** `$ 603.598.644`
    *   **Descripción:** Deudas con bancos u otras instituciones financieras que deben ser pagadas en menos de un año.
    *   **Implicancia en el juego:** Esta es una obligación financiera significativa que generará gastos por intereses y requerirá pagos de capital, presionando la liquidez de la empresa.
*   **Cuentas y Documentos por Pagar:** `$ 146.466.667`
    *   **Descripción:** Monto que la empresa debe a sus proveedores por la compra de materias primas o servicios.
    *   **Implicancia en el juego:** El jugador debe gestionar estos pagos para mantener una buena relación con los proveedores.
*   **Impuestos por Compra/Venta (IVA):** `$ 146.893.242`
    *   **Descripción:** Probablemente representa el IVA Débito Fiscal (por ventas) que supera al IVA Crédito Fiscal (por compras), resultando en un monto a pagar al fisco.
*   **Impuesto a la Renta:** `$ 26.051.546`
    *   **Descripción:** Provisión del impuesto a la renta sobre las utilidades del período anterior, pendiente de pago.
*   **Dividendos por Pagar:** `$ 86.897.854`
    *   **Descripción:** Utilidades que la empresa se comprometió a repartir a sus accionistas pero que aún no ha pagado.
*   **Notas de Crédito:** `$ 4.724.860`
    *   **Descripción:** Representa una obligación con clientes, usualmente por devoluciones de productos.

### 3.3. Patrimonio (El valor neto de la empresa)

*   **Capital Pagado:** `$ 430.318.389`
    *   **Descripción:** Es el aporte inicial de dinero y recursos que los socios (accionistas) realizaron para constituir la empresa.
    *   **Implicancia en el juego:** Representa la base del valor de la empresa que pertenece a los dueños. El objetivo del jugador es aumentar el valor total del patrimonio.

### 3.4. Resumen de la Ecuación Contable

La situación inicial muestra una empresa operativa con un nivel de endeudamiento considerable en el corto plazo. La gestión del flujo de caja para pagar estas deudas será el primer gran desafío del jugador.

**Activo Total ≈ Pasivo Total + Patrimonio**

## 4. Ciclo Operacional y Flujo del Juego

El juego se desarrolla en una secuencia de "períodos" (turnos), que representan un ciclo completo de negocio (ej. un trimestre o un año). En cada período, el jugador debe analizar la situación de la empresa, tomar un conjunto de decisiones y luego avanzar al siguiente período para ver los resultados.

El flujo de juego en un período típico se puede dividir en las siguientes fases:

### 4.1. Fase de Análisis (Inicio del Período)

El jugador comienza revisando los resultados del período anterior. Las interfaces de "Consulta" son fundamentales en esta fase:
*   **Consulta de Estados Financieros:** Se revisan el Balance Final, Estado de Resultados y Flujo de Caja del período anterior para entender la salud financiera de la empresa.
*   **Análisis de Decisiones Pasadas:** Se pueden consultar los precios de materia prima que se pagaron, las ventas que se proyectaron vs. las reales, etc.

### 4.2. Fase de Toma de Decisiones

Esta es la fase principal donde el jugador, actuando como gerente, define la estrategia para el período actual. Las decisiones se toman a través de diversas interfaces:

#### Decisiones de Operaciones y Marketing:
*   **Compras y Producción (`preciomateriaprima.py`, `datosfisicosdeinventario.py`):**
    *   Definir cuánto pagar por la materia prima.
    *   Decidir la cantidad de unidades a producir, lo que impacta los niveles de inventario de productos en proceso y terminados.
*   **Precios y Ventas (`ventaproyectada.py`, `ventasporpais.py`):**
    *   Establecer el precio de venta de los productos.
    *   Proyectar la cantidad de unidades que se espera vender.
    *   Distribuir las ventas entre diferentes mercados (países).
*   **Marketing e Inteligencia (`publicidad.py`, `investigacionmercado.py`):**
    *   Asignar un presupuesto para publicidad, lo que probablemente impacta la demanda.
    *   Invertir en investigación de mercado para obtener información que ayude a tomar mejores decisiones de precio y producción.

#### Decisiones Financieras:
*   **Gestión de Caja y Deuda (`caja.py`, `prestamo.py`):**
    *   Gestionar el efectivo disponible.
    *   Decidir si solicitar nuevos préstamos (de corto o largo plazo) para financiar operaciones o inversiones.
    *   Realizar pagos de deudas existentes.
*   **Política de Dividendos (inferido de `informacionadicionalbalance.py` y `balance_inicial.json`):**
    *   Decidir qué porcentaje de las utilidades del período anterior se repartirá a los accionistas como dividendos.

### 4.3. Fase de Procesamiento (Fin del Período)

Una vez que el jugador ha ingresado todas sus decisiones, se finaliza el período. En este punto, el motor de simulación del juego procesa toda la información:
1.  **Calcula los resultados:** Se determinan las ventas reales (posiblemente afectadas por el precio, la publicidad y factores de mercado), los costos de producción, los gastos operativos y los resultados financieros.
2.  **Genera los nuevos estados financieros:** El sistema actualiza el Balance General, el Estado de Resultados y el Flujo de Caja.
3.  **Avanza al siguiente período:** El Balance Final del período actual se convierte en el Balance Inicial del siguiente, y el ciclo vuelve a comenzar.

Este ciclo se repite hasta completar el número total de períodos del juego, momento en el que se evalúa el desempeño final del jugador.

## 5. Componentes Clave del Modelo de Negocio

### 5.1. Modelo de Ingresos

La fuente de ingresos principal de la empresa es la **venta de productos manufacturados**. Los ingresos se determinan por la cantidad de unidades vendidas multiplicada por el precio de venta unitario. El jugador tiene control sobre:
*   **Fijación de Precios (`ventaproyectada.py`):** Decidir el precio de los productos es una de las palancas más importantes para gestionar la rentabilidad y la demanda.
*   **Estrategia de Mercado (`ventasporpais.py`):** La empresa puede vender en múltiples mercados (países), lo que sugiere que el jugador debe adaptar su estrategia a las condiciones de cada región. La demanda en cada mercado puede estar influenciada por la publicidad, el precio y factores económicos externos.

### 5.2. Estructura de Costos

La empresa tiene una estructura de costos típica de una compañía manufacturera:

*   **Costo de Ventas (Costo de los bienes vendidos):**
    *   **Materia Prima (`preciomateriaprima.py`):** Costo de los insumos necesarios para la producción.
    *   **Costos de Producción:** Incluye la mano de obra directa y los costos indirectos de fabricación (CIF) asociados a la operación de las plantas.
*   **Gastos de Operación (Gastos de Administración y Ventas):**
    *   **Marketing y Publicidad (`publicidad.py`):** Inversión para impulsar la demanda.
    *   **Investigación de Mercado (`investigacionmercado.py`):** Gasto para obtener información estratégica.
    *   **Depreciación (`balance_inicial.json`):** Gasto no monetario por el desgaste de los activos fijos (plantas, edificios, etc.).
*   **Gastos Financieros:**
    *   **Intereses sobre Préstamos (`prestamo.py`):** Costo del financiamiento obtenido de terceros.
*   **Impuestos:**
    *   **Impuesto al Valor Agregado (IVA):** El juego simula el IVA, gestionando el crédito fiscal (por compras) y el débito fiscal (por ventas).
    *   **Impuesto a la Renta:** La empresa debe pagar un impuesto sobre sus utilidades, de acuerdo con la tasa impositiva vigente.

### 5.3. Gestión Financiera

El jugador debe tomar decisiones financieras clave que afectan la solvencia y liquidez de la empresa:

*   **Gestión del Capital de Trabajo:**
    *   **Caja (`caja.py`):** Administrar el efectivo para asegurar el pago de obligaciones.
    *   **Cuentas por Cobrar y por Pagar:** Gestionar los plazos de cobro a clientes y de pago a proveedores.
*   **Decisiones de Financiamiento (`prestamo.py`):**
    *   El jugador puede solicitar **préstamos a corto y largo plazo** para financiar el crecimiento, las operaciones o cubrir déficits de caja.
    *   Debe gestionar el pago de la deuda existente para evitar el default.
*   **Política de Dividendos:**
    *   El jugador decide qué porción de las utilidades se reinvierte en la empresa y qué porción se distribuye a los accionistas.

### 5.4. Entorno Económico y Variables Chilenas

Una característica distintiva del juego es su anclaje a la economía chilena a través de dos variables clave:

*   **Unidad de Fomento (UF) (`Datos/uf.py`):**
    *   **Función:** Es una unidad de cuenta reajustable por la inflación. En el juego, es probable que deudas a largo plazo, contratos importantes o incluso el valor de ciertos activos estén expresados en UF.
    *   **Impacto Contable:** La variación de la UF obliga a realizar una **"Corrección Monetaria"** de las partidas no monetarias del balance, generando ganancias o pérdidas por inflación que impactan el Estado de Resultados. Esto simula de manera realista el efecto de la inflación en las finanzas de una empresa chilena.
*   **Unidad Tributaria Mensual (UTM) (`Datos/utm.py`):**
    *   **Función:** Es una unidad de cuenta utilizada para fines tributarios y de multas.
    *   **Impacto en el Juego:** El cálculo y pago de impuestos, como el Impuesto a la Renta, probablemente esté vinculado al valor de la UTM del período correspondiente.

La capacidad de actualizar estos valores desde el Banco Central de Chile (`bcchapi`) permite que el juego simule las condiciones económicas reales del momento en que se juega.
