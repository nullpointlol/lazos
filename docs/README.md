# Documentación LAZOS

Índice de documentación técnica del proyecto LAZOS.

---

## 📖 Para Agentes IA

**⭐ EMPEZAR AQUÍ:**

### [Guía Completa para Agentes IA](/docs/ai/COMPREHENSIVE_GUIDE.md)

Documentación exhaustiva y centralizada que cubre:

- **Sección 1:** Origen y visión del proyecto
- **Sección 2:** Arquitectura técnica (stack, estructura de directorios)
- **Sección 3:** Estado actual completo (features implementadas y pendientes)
- **Sección 4:** Modelos de datos (diagramas ER, índices)
- **Sección 5:** API Backend (endpoints, schemas, ejemplos)
- **Sección 6:** Frontend (páginas, componentes, hooks)
- **Sección 7:** Flujos principales de usuario
- **Sección 8:** Configuración y deployment
- **Sección 9:** Decisiones de arquitectura
- **Sección 10:** Próximos pasos y roadmap
- **Apéndices:** Troubleshooting, glosario, checklists

**Total:** ~2,000 líneas de documentación técnica completa.

---

## 📚 Para Desarrolladores Humanos

- **[README Principal](../README.md)** - Quickstart, instalación, comandos básicos
- **[CHANGELOG](../CHANGELOG.md)** - Historial de cambios por versión
- **[API Reference](http://localhost:8000/docs)** - Swagger UI (generado automáticamente por FastAPI)

---

## 🎯 Cómo Usar Esta Documentación

### Si eres un Agente IA

1. **Lee la [Guía Completa](/docs/ai/COMPREHENSIVE_GUIDE.md)** de principio a fin
2. Consulta secciones específicas según la tarea (ver índice en el documento)
3. **IMPORTANTE:** Actualiza la guía cuando hagas cambios significativos:
   - Nuevas features → Sección 3 (Estado Actual) + Sección 10 (Roadmap)
   - Cambios en API → Sección 5 (API Backend)
   - Nuevos componentes → Sección 6 (Frontend)
   - Bugs arreglados → Remover de Sección 3.2 (Features No Implementadas)
   - Decisiones de arquitectura → Sección 9

### Si eres un Desarrollador Humano

1. **Instalación:** Sigue el [README.md](../README.md)
2. **Desarrollo:** Consulta la [Guía Completa](/docs/ai/COMPREHENSIVE_GUIDE.md) para entender arquitectura
3. **Debugging:** Ver Apéndice A de la Guía Completa (Troubleshooting)
4. **Contribuir:** Ver sección "Contribuir" en README.md

---

## 📁 Estructura de Documentación

```
docs/
├── README.md                           # Este archivo (índice)
└── ai/
    └── COMPREHENSIVE_GUIDE.md          # Guía completa para agentes IA
```

**NOTA:** Toda la documentación técnica ha sido consolidada en `COMPREHENSIVE_GUIDE.md` para eliminar duplicación y mantener una única fuente de verdad.

---

## ✅ Checklist de Mantenimiento

### Al agregar una feature:

- [ ] Actualizar `COMPREHENSIVE_GUIDE.md` → Sección 3 (Estado Actual)
- [ ] Actualizar `../CHANGELOG.md` con entry
- [ ] Si cambia API → Actualizar Sección 5 (API Backend)
- [ ] Si cambia frontend → Actualizar Sección 6 (Frontend)
- [ ] Actualizar Sección 10 (Roadmap): mover de "En Progreso" a "Implementado"

### Al arreglar un bug:

- [ ] Actualizar `../CHANGELOG.md` en sección "Fixed"
- [ ] Si estaba documentado → Remover de Sección 3.2 (Features No Implementadas)

### Al hacer cambios arquitectónicos:

- [ ] Documentar decisión en Sección 9 (Decisiones de Arquitectura)
- [ ] Actualizar diagramas si aplica

---

## 📞 Contacto

Para preguntas sobre documentación, [abrir issue en GitHub](https://github.com/tu-usuario/lazos/issues).

---

**Última actualización:** 2025-12-29
**Mantenido por:** Agentes IA + Claude Code
