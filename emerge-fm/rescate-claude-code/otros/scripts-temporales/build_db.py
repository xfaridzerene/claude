# -*- coding: utf-8 -*-
import csv, json, io
from collections import Counter

# ---------------------------------------------------------------------------
# Modelo de puntaje P.A.R.A.C. (0-100)
#   P  = Poder de pago                      (0-25)
#   A  = Afinidad con la audiencia          (0-25)  80s/90s + noticias, 30-60 anios
#   R  = Recompra / ciclo de compra local   (0-20)
#   A2 = Acceso al decisor                  (0-20)  duenio local vs central en Santiago
#   C  = Capacidad de canje / premios       (0-10)
# ---------------------------------------------------------------------------

rows = [
 ("Cámara Regional de Comercio, Servicios y Turismo de Rancagua y O'Higgins","Gremio empresarial","Rancagua","Presidente Germán Riesco 177","(72) 2585710 / (72) 2845955","facebook.com/camararegional",18,24,16,20,9,"NO es un auspiciador: es la llave maestra. Ofrecer un espacio semanal gratis \"La voz del comercio\" a cambio de acceso al directorio de socios y de una presentación ante el directorio. Cumplió 100 años en 2025.","elrancaguino.cl / mercantil.com"),
 ("Funeraria Riquelme","Servicios funerarios","Rancagua","M. A. Matta 349 / Av. L. B. O'Higgins 1009","(72) 2223935 / (72) 2641385 / +56 9 9881 6140","—",21,25,18,20,5,"Rubro histórico de la radio adulta. Vender presencia permanente 24/7 con frase de servicio. Decide el dueño y el ciclo de compra es inmediato.","mercantil.com / defunerarias.info"),
 ("Funerales Rodríguez","Servicios funerarios","Rancagua","Pedro Emilio Cuadra 120","(72) 2238002","—",20,25,18,20,5,"Mismo pitch que Riquelme. Ofrecer exclusividad de rubro por 6 meses como argumento de urgencia.","mercantil.com"),
 ("Fábrica y Funeraria Renacer","Servicios funerarios","Rancagua","M. A. Matta 376","(72) 2237020 / +56 9 8549 7265","—",19,25,18,20,5,"Fabrican sus propios ataúdes: margen alto, buen candidato a plan mensual completo.","mercantil.com"),
 ("Funerales Paz","Servicios funerarios","Rancagua","M. A. Matta 197","+56 9 3391 8289","—",17,24,18,20,5,"Plan de entrada $80.000 con 3 frases diarias. Cierre rápido por WhatsApp.","defunerarias.info"),
 ("Funeraria Rancagua VI","Servicios funerarios","Rancagua","(por confirmar)","+56 9 4891 6839","facebook.com/people/Funeraria-Rancagua-VI",15,23,18,20,5,"Promociona \"servicios desde $0\" con cuota mortuoria IPS/AFP: mensaje perfecto para radio hablada.","Facebook"),
 ("Casa Zúñiga","Multitienda regional / crédito propio","Rancagua","Juan Nicolás Rubio 348 (casa matriz) + Rengo y Santa Cruz","(72) 2331100","casazuniga.cl / IG @casazuniga.cl",24,24,17,16,7,"Multitienda regional con tarjeta propia y público adulto de la zona. El auspiciador soñado: presupuesto real y decisión en Rancagua. Pedir reunión con gerencia comercial.","casazuniga.cl / latinoplaces.com"),
 ("Clínica Isamédica","Salud privada","Rancagua","Carretera El Cobre Pdte. E. Frei Montalva 884","(72) 2200000 / WhatsApp +56 9 5370 4113","clinicaisamedica.cl",25,23,15,13,6,"Clínica local desde 1995 con convenios Fonasa PAD. Vender una cápsula de salud dentro del programa en vivo, no solo frases.","clinicaisamedica.cl / superdesalud.gob.cl"),
 ("Hospital Clínico FUSAT","Salud privada","Rancagua","Carretera El Cobre 1002","(72) 2204100","fusat.cl",25,22,14,11,6,"Ligado históricamente a El Teniente: audiencia exacta de la radio. Ciclo de decisión largo, entrar por Comunicaciones o Marketing.","fusat.cl / mercantil.com"),
 ("Clínica Central Odontológica","Salud dental","Rancagua","O'Carrol 819","(72) 2222800","clinicaodontologica.cl",21,23,17,17,6,"Implantes y ortodoncia = ticket alto que necesita flujo constante de pacientes. Ofrecer promoción medible con código EMERGE.","clinicaodontologica.cl"),
 ("Centro Dental España","Salud dental","Rancagua","Avenida España 540","(72) 2221349","—",19,23,17,18,6,"Pyme dental con decisión del dueño. Plan de entrada más canje parcial (blanqueamiento como premio al aire).","mercantil.com"),
 ("Centro de Especialidades Odontológicas","Salud dental","Rancagua","(por confirmar)","(72) 2227959 / +56 9 9742 1325","contacto@centrodeespecialidadesodontologicas.cl",19,23,17,18,6,"Tienen email público: partir con propuesta escrita y seguimiento telefónico a las 48 horas.","centrodeespecialidadesodontologicas.cl"),
 ("Clínica Dental Santa Antonia","Salud dental","Rancagua","Av. Capitán Ramón Freire 76","(por confirmar en sitio)","clinicasantaantonia.cl",19,23,17,17,6,"Urgencia dental 24 horas: mensaje de servicio ideal para frases nocturnas y de fin de semana.","clinicasantaantonia.cl"),
 ("Clínica Dental Rancagua","Salud dental","Rancagua","Centro de Rancagua","(por confirmar en sitio)","dentalrancagua.cl",18,23,17,17,6,"40 años en la ciudad: pitch de \"dos marcas con historia en Rancagua\".","dentalrancagua.cl"),
 ("Clínica CleverSalud / Clever Gym","Salud + gimnasio","Rancagua","Cáceres 630, Cachapoal","(72) 2846500","cleversalud.cl / IG @clevergym",21,22,16,15,7,"Dos unidades de negocio en una sola visita (clínica y gimnasio nuevo). Proponer paquete combinado con descuento.","cleversalud.cl"),
 ("Centro Oftalmológico Clínica Visión","Salud visual","Rancagua","Av. Bello Horizonte 781, Torre C, piso 3","(72) 2283100","clinicavision.cl",21,24,16,15,6,"Público 45+ que escucha radio: cataratas y presbicia. Altísima afinidad con la audiencia.","clinicavision.cl / superdesalud.gob.cl"),
 ("Centro Oftalmológico Láser","Salud visual","Rancagua","Carretera del Cobre 1330","(72) 2643640","centrooftalmologicolaser.cl",20,24,16,14,6,"Mismo argumento etario. Ofrecer mención dentro del bloque de noticias de salud.","mercantil.com"),
 ("Centro Oftalmológico del Libertador","Salud visual","Rancagua","Astorga 165","(72) 2217840","—",19,24,16,15,6,"Pyme médica céntrica, decisión rápida.","mercantil.com"),
 ("Centro Oftalmológico Ruiz & Portus","Salud visual","Rancagua","El Cardal 787 (frente a Portal Rancagua)","+56 9 3430 2077","IG @centro.oftaruizoportus",18,23,16,17,6,"Activos en Instagram: vender el combo aire + redes sociales de la radio.","Instagram"),
 ("CEOFT Clínica Oftalmológica","Salud visual","Rancagua","(por confirmar)","(72) 2359800","ceoft.cl",19,23,16,13,6,"Contactar por formulario web y luego llamar.","ceoft.cl"),
 ("Automotora Alameda (DFSK)","Automotriz","Rancagua","Cachapoal 1179","+56 72 260 8780","automotorasenchile.com",22,24,16,16,6,"Concesionario con marca propia y servicio técnico. La radio sigue vendiendo autos en regiones: pedir campaña de fin de mes.","automotorasenchile.com"),
 ("Automotora Rancagua (Marco Yáñez Langer)","Automotriz","Rancagua","O'Higgins 0214","+56 9 8808 3279","automotorarancagua.com",19,24,16,19,6,"Automotora de dueño: el decisor contesta su propio teléfono. Cierre posible en una sola visita.","automotorarancagua.com"),
 ("Automotora Mardones","Automotriz","Rancagua","Avenida San Martín 718, oficina","(por confirmar)","mundochileno.com",18,24,16,18,6,"Usados: rotación alta de stock, necesita avisaje permanente.","mundochileno.com"),
 ("Coseche Rancagua","Automotriz (concesionario)","Rancagua","Av. Libertador Gral. B. O'Higgins 27","600 490 3000","automotorasenchile.com",23,23,15,9,6,"Presupuesto grande pero decisión centralizada. Entrar con propuesta de campaña puntual (liquidación o lanzamiento).","automotorasenchile.com"),
 ("Ferrobal","Ferretería / construcción","Rancagua","San Martín 155","(72) 2230002","ferreteriass.cl",20,24,18,17,7,"Ferretería local fuerte: cliente maestro y jefe de hogar, audiencia idéntica a la radio. Canje posible en materiales para el estudio.","ferreteriass.cl"),
 ("Ferretería P.V.C.","Ferretería / construcción","Rancagua","Millán 456","(72) 2226180","—",17,24,18,19,7,"Pyme de barrio con dueño presente. Plan de entrada $60.000 más canje.","mercantil.com"),
 ("Ferretería Persa","Ferretería / construcción","Rancagua","Millán 45","+56 9 3951 0685","facebook.com/FerreteriaPersa.cl",16,24,18,19,7,"Activa en Facebook y responde por WhatsApp: contacto directo sin filtros.","Facebook"),
 ("3V Comercial","Ferretería / comercial","Rancagua","Manuel Rodríguez 650","+56 9 9336 2305 / (72) 2767534","3v.cl",19,23,18,17,7,"Empresa comercial con sitio propio: probablemente ya invierte en marketing.","3v.cl"),
 ("Construmart Rancagua","Ferretería (cadena nacional)","Rancagua","Miguel Ramírez 1193","(2) 3293 0870","construmart.cl",24,22,17,7,5,"Presupuesto alto pero decide Santiago. Solo vale la pena vía jefe de local para campañas de temporada.","ferreteriass.cl"),
 ("Hospital Veterinario Arrayán","Veterinaria","Rancagua y Machalí","Sucursales en ambas comunas","(72) 2212044 Rcg / (72) 2281626 Mch","arrayanveterinaria.cl",20,22,18,16,8,"Urgencias 24/7 en dos comunas: cubre justo el territorio de la radio. Ideal para una cápsula de mascotas semanal.","arrayanveterinaria.cl"),
 ("Clínica Veterinaria Family Vet","Veterinaria","Machalí y Rancagua","Pje. Bahía de San Vicente 717, Machalí / L. B. O'Higgins 01487, Rancagua","(72) 2279196 / (72) 2374884","—",18,22,18,17,8,"Atiende de 00:00 a 24:00: mensaje de urgencia con alto valor percibido.","agendapro.com"),
 ("Clínica Veterinaria Hannover","Veterinaria","Rancagua","Av. República de Chile 067","(por confirmar)","—",16,21,18,18,8,"Plan de entrada más sorteo de consulta gratis en programa en vivo.","infoisinfo.cl"),
 ("Veterinaria VetCenter","Veterinaria","Rancagua","Av. Alberto Einstein 339","(72) 2820087","—",16,21,18,18,8,"Mismo esquema que Hannover.","infoisinfo.cl"),
 ("Hospital Veterinario Central","Veterinaria","Rancagua","Av. Héctor Zamorano 906, sector Manzanal","(por confirmar)","—",16,21,18,17,8,"Sector residencial en crecimiento.","infoisinfo.cl"),
 ("Hotel Termas de Cauquenes","Turismo / hotel / eventos","Machalí","Camino Termas de Cauquenes s/n","+56 9 9323 3379","alvaro@htdc.cl / htdc.cl",21,25,14,19,10,"Ícono turístico de Machalí con público adulto regional y contacto directo por email. El mejor candidato a CANJE (estadías y spa como premios al aire).","htdc.cl / sernatur.cl"),
 ("Centro de Eventos Casona de Machalí","Eventos / banquetería","Machalí","Machalí","(por confirmar)","IG @casonamachali",17,23,15,18,10,"Matrimonios y eventos de empresa. Canje de arriendo de salón por campaña. Público 30-60: la audiencia 80s/90s exacta.","Instagram / invitalo.cl"),
 ("La Hacienda de Machalí","Restaurante","Machalí","El Pueblito de Machalí","(por confirmar)","lahaciendarestaurante.cl / IG @lahaciendamachali",16,23,17,18,10,"Gastronomía chilena, público familiar de fin de semana. Canje de consumo más auspicio del programa del sábado.","lahaciendarestaurante.cl"),
 ("Weiser Corredora de Propiedades","Inmobiliaria","Rancagua / Machalí","(oficina por confirmar)","+56 9 3134 2040","hola@weiser.cl / weiser.cl",19,23,14,18,6,"Opera justo en Rancagua-Machalí. Email público: enviar propuesta escrita directa.","weiser.cl"),
 ("Ana María Lillo & Marcela Quintanilla Propiedades","Inmobiliaria","Rancagua / Machalí","Loma la Patagua 1232, Rancagua","+56 9 6577 4061","contacto@anamarialillo.cl",19,23,14,19,6,"50 años en el mercado local: pitch de trayectoria compartida con la radio.","anamarialillo.cl / toppropiedades.cl"),
 ("Silvia Correa Baeza Servicios Inmobiliarios","Inmobiliaria","Rancagua","Avda. Brasil 850, oficina 102","(72) 2227781 / +56 9 9818 8545","silviacorreabaeza@gmail.com",17,23,14,19,6,"Corredora individual: decisión inmediata, ideal para plan de entrada.","silviacorreabaeza.cl"),
 ("Correa & Schmidt (Casas Rancagua)","Inmobiliaria","Rancagua / Machalí","(por confirmar)","(vía formulario web)","casasrancagua.cl",18,23,14,17,6,"Contactar por formulario y luego llamar.","casasrancagua.cl"),
 ("Propiedades Machalí","Inmobiliaria","Machalí","Machalí","+56 9 9797 4036","facebook.com/PropiedadesMachali",15,22,14,19,6,"Foco 100% Machalí: puede auspiciar solo el bloque de la mañana.","Facebook"),
 ("Centro Machalí (centro comercial)","Administración centro comercial","Machalí","Centro de Machalí","(por confirmar)","centromachali.cl",19,23,16,15,8,"Tiene 28 locales comerciales. Vender un \"pack galería\": campaña paraguas más descuento a cada local. Un contacto, muchos clientes.","centromachali.cl"),
 ("Ilustre Municipalidad de Machalí","Municipio / avisaje institucional","Machalí","Plaza de Armas 11","(72) 2746700 / (72) 2746701","machali.cl / IG @munimachali",22,24,12,12,7,"Avisaje institucional y campañas comunales (seguridad, salud, eventos). Requiere inscribirse como proveedor y postular a licitaciones: proceso lento pero contrato grande.","machali.cl"),
 ("Taller Mecánico RMH","Automotriz / servicio","Rancagua","Avenida Uruguay 126, Rancagua Oriente","+56 9 9694 0930","tallermecanico.top",15,23,18,19,7,"Alineación, frenos y scanner: servicios de recompra frecuente. Plan de entrada perfecto.","tallermecanico.top"),
 ("Repuestos Lubritodo","Repuestos automotrices","Rancagua","José Victorino Lastarria 409","(72) 2233370","—",16,23,18,18,6,"Repuestos: público masculino 35+, núcleo duro de la audiencia 80s/90s.","mercantil.com"),
 ("Lubricentro Taller Mecánico Sointra","Automotriz / servicio","Rancagua","Padre Hurtado 1, La Granja","+56 9 6965 5767 / +56 9 3402 0780","sointra.cl",15,22,18,19,7,"Cambio de aceite: recordatorio cada 3 meses, mensaje ideal para frase corta.","mercantil.com / sointra.cl"),
 ("MG Automotriz","Automotriz / servicio","Rancagua","(por confirmar)","+56 9 7608 5600","mg-automotriz.ueniweb.com",14,22,18,19,7,"Pyme de dueño, cierre por WhatsApp.","ueniweb.com"),
 ("Comercial Millán","Lubricentro / repuestos","Rancagua","(por confirmar)","(por confirmar)","comercialmillan.cl",16,22,18,17,6,"Tiene sitio web propio: ya invierte en presencia comercial.","comercialmillan.cl"),
 ("Gym Factory Rancagua","Gimnasio","Rancagua","Membrillar 266","+56 9 5655 9208","IG @gymfactory.cl / wellhub.com",14,19,17,19,9,"Convenio con Wellhub: tiene estructura formal. Canje de membresías como premio.","wellhub.com"),
 ("Energy Fitness Club Rancagua","Gimnasio","Rancagua","(por confirmar)","+56 9 7699 5228","IG @energyclubrancagua",13,19,17,19,9,"Campañas de enero y marzo (vuelta a la rutina).","Instagram"),
 ("Gimnasio Pacific Rancagua","Gimnasio (cadena)","Rancagua","(por confirmar)","(por confirmar)","gimnasiopacific.cl",17,19,17,11,8,"Cadena: decisión fuera de la región, pero el jefe de sede maneja un presupuesto local pequeño.","gimnasiopacific.cl"),
 ("Wolf Gym Rancagua","Gimnasio","Rancagua","(por confirmar)","(vía Instagram)","IG @wolfgymrancagua",11,18,17,19,9,"Solo canje o plan mínimo. Útil para llenar parrilla al inicio.","Instagram"),
 ("VitalFit Rancagua","Gimnasio","Rancagua","(por confirmar)","(vía Instagram)","IG @vitalfit_cl",11,18,17,19,9,"Igual que Wolf Gym.","Instagram"),
 ("Central Gym Rancagua","Gimnasio","Rancagua","(por confirmar)","(vía Instagram)","IG @central_gymrancagua",11,18,17,19,9,"Igual que Wolf Gym.","Instagram"),
 ("Outlet Lourdes","Hogar / retail","Rancagua","Avenida Diagonal Doñihue 2355","+56 9 3788 4464","outlet-lourdes.ueniweb.com",14,22,18,19,8,"Textil y hogar de precio bajo: el mensaje de oferta semanal funciona muy bien en radio.","ueniweb.com"),
 ("La Casita del Mueble","Muebles","Rancagua","Av. Río Loco","+56 9 7359 9597","la-casita-del-mueble.ueniweb.com",13,22,15,19,8,"Muebles a medida: ticket alto y poco volumen. Plan de entrada.","ueniweb.com"),
 ("Supermercado Ramírez","Supermercado local","Machalí","Arturo Prat, Machalí","(72) 241 12xx (por confirmar)","mundochileno.com",17,24,19,18,8,"Supermercado de dueño en Machalí: ofertas semanales al aire y canje en abarrotes para concursos.","mundochileno.com"),
 ("Comercial Urimo Ltda. (minimarket)","Minimarket","Machalí","Arturo Prat 21, Machalí","(72) 241 27xx (por confirmar)","mundochileno.com",13,23,19,19,8,"Comercio de barrio: plan de entrada $50.000 con 3 frases diarias.","mundochileno.com"),
 ("Boss Bikes","Bicicletas / deporte","Machalí","Los Naranjos 966, Machalí","(72) 2488107","—",13,21,16,19,8,"Ciclismo recreativo adulto en Machalí. Canje de mantenciones como premio.","directorio comercial local"),
 ("Acuña e Hijos S.A.","Minería / construcción / montaje","Rancagua","Avenida La Compañía 038, Villa Magisterio","(por confirmar)","acunaehijos.cl",22,20,10,14,5,"B2B minero para Codelco El Teniente. No busca clientes por radio, pero sí imagen local y personal: venderle marca empleadora y avisos de postulación.","acunaehijos.cl"),
 ("Instituto Profesional Santo Tomás - Sede Rancagua","Educación superior","Rancagua","Sede Rancagua","(2) 2496 5280 / 2496 5287","ipsantotomas.cl",21,21,11,10,6,"Campaña de admisión de octubre a marzo. Presupuesto nacional, pero la sede pide apoyo regional: contactar a Marketing de sede.","ipsantotomas.cl"),
 ("Cpech Rancagua","Preuniversitario","Rancagua","Sede Rancagua","(por confirmar)","cpech.cl",18,20,11,9,6,"Solo temporada de matrículas. Proponer campaña puntual de 2 semanas.","cpech.cl"),
 ("Clínica Dental Santa Blanca - Rancagua","Salud dental (cadena)","Rancagua","Sede Rancagua","(por confirmar)","clinicasantablanca.cl",19,22,17,9,5,"Cadena con decisión centralizada: baja prioridad frente a las dentales locales.","clinicasantablanca.cl"),
 ("Uno Salud Dental Rancagua","Salud dental (cadena)","Rancagua","Sede Rancagua","(por confirmar)","unosalud.cl",20,22,17,8,5,"Igual que Santa Blanca.","unosalud.cl"),
 ("Domain Barber Studio","Barbería","Machalí","Centro de Machalí","(reserva online)","domainbarbersstudio.setmore.com",10,17,18,19,9,"Solo canje o plan mínimo. Buen generador de contenido para las redes de la radio.","setmore.com"),
 ("Dark Side Barber Shop","Barbería","Machalí","Machalí","(vía Facebook)","facebook.com/darksidebshop",9,17,18,19,9,"Igual que Domain.","Facebook"),
]

def tier(score):
    if score >= 84:
        return "A · Ronda 1 (semanas 1-3)"
    if score >= 78:
        return "B · Ronda 2 (semanas 4-8)"
    return "C · Canje o plan de entrada"

def plan(P):
    if P >= 22:
        return "300 frases $500.000 o Programa $150.000"
    if P >= 18:
        return "150 frases $300.000 o Programa $150.000"
    if P >= 14:
        return "L-V 100 frases $200.000 o Entrada $100.000"
    return "Entrada $50.000-$80.000 o canje"

data = []
for (nom, rub, com, dire, tel, web, P, A, R, A2, C, gancho, fuente) in rows:
    s = P + A + R + A2 + C
    data.append(dict(nombre=nom, rubro=rub, comuna=com, direccion=dire, telefono=tel, web=web,
                     P=P, A=A, R=R, A2=A2, C=C, score=s, tier=tier(s), plan=plan(P),
                     gancho=gancho, fuente=fuente))

data.sort(key=lambda d: (-d["score"], d["nombre"]))

out = "C:/Users/farid/Desktop/Base_Auspiciadores_EmergeFM.csv"
with io.open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["#", "Empresa", "Rubro", "Comuna", "Dirección", "Teléfono", "Web / Email / Instagram",
                "Pago (25)", "Afinidad (25)", "Recompra (20)", "Acceso decisor (20)", "Canje (10)",
                "PUNTAJE (100)", "Prioridad", "Plan sugerido", "Gancho de venta", "Fuente del dato",
                "Dato verificado", "Estado gestión", "Fecha contacto", "Próximo paso", "Notas"])
    for i, d in enumerate(data, 1):
        w.writerow([i, d["nombre"], d["rubro"], d["comuna"], d["direccion"], d["telefono"], d["web"],
                    d["P"], d["A"], d["R"], d["A2"], d["C"], d["score"], d["tier"], d["plan"],
                    d["gancho"], d["fuente"], "Por confirmar", "Sin contactar", "", "", ""])

with io.open("C:/Users/farid/AppData/Local/Temp/claude/C--Users-farid-Desktop-claude-code/2650f179-0c9f-4e30-b201-228e19538865/scratchpad/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print("Total empresas:", len(data))
print(Counter(d["tier"] for d in data))
print("Rancagua:", sum(1 for d in data if "Rancagua" in d["comuna"]),
      "| Machali:", sum(1 for d in data if "Machal" in d["comuna"]))
for d in data[:20]:
    print(d["score"], "|", d["nombre"], "|", d["plan"])
