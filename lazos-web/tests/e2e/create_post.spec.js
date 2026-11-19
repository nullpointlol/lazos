// lazos-web/tests/e2e/create_post.spec.js
import { test, expect } from '@playwright/test';
import path from 'path';

test('Debería crear una publicación usando autocompletado por IA y ubicación manual en Buenos Aires', async ({ page }) => {
  // Aumentar el timeout para el análisis con IA (puede tomar un tiempo en llamar a Cloudflare)
  test.setTimeout(120000);

  // Registrar respuestas de la API para depuración
  page.on('response', async (response) => {
    if (response.url().includes('analyze-image')) {
      try {
        const json = await response.json();
        console.log('--- RESPUESTA DE ANALYZE-IMAGE ---');
        console.log(JSON.stringify(json, null, 2));
        console.log('---------------------------------');
      } catch (e) {
        console.error('Error parseando respuesta de analyze-image:', e);
      }
    }
  });

  // 1. Navegar a la página de creación de posts
  await page.goto('/new');

  // Asegurar que la página cargó correctamente
  await expect(page.locator('h2')).toHaveText('Nuevo avistamiento');

  // 2. Subir la imagen de prueba con texto
  const imagePath = path.resolve(process.cwd(), '../lazos-api/tests/fixtures/img_test_with_text.jpg');
  console.log('Subiendo imagen de prueba desde:', imagePath);
  
  // Establecer el archivo en el input hidden de tipo file
  await page.setInputFiles('input[type="file"]', imagePath);

  // Esperar a que comience el análisis con IA
  await expect(page.locator('text=Analizando imagen con IA')).toBeVisible();

  // Esperar a que el análisis termine (el mensaje desaparece)
  await expect(page.locator('text=Analizando imagen con IA')).not.toBeVisible({ timeout: 45000 });

  // 3. Validar que la información se autocompletó correctamente
  // - Animal Type (Perro debería estar seleccionado con la clase bg-primary)
  await expect(page.locator('button', { hasText: '🐕 Perro' })).toHaveClass(/bg-primary/);

  // - Sexo (Macho debería estar seleccionado con la clase bg-primary)
  await expect(page.locator('button', { hasText: '♂ Macho' })).toHaveClass(/bg-primary/);

  // - Tamaño (Chico debería estar seleccionado con la clase bg-primary)
  await expect(page.locator('button', { hasText: 'Chico' })).toHaveClass(/bg-primary/);

  // - Contacto (autocompletado con el número extraído)
  await expect(page.locator('#contact')).toHaveValue(/96.*467/);

  // - Descripción (autocompletada con texto de OCR y descripción visual)
  await expect(page.locator('#description')).toContainText('SAM');
  await expect(page.locator('#description')).toContainText('pug');

  // Reemplazar la descripción por una limpia (sin teléfonos/números repetidos) para pasar la validación local del frontend
  await page.locator('#description').fill('Se busca perro pug marrón llamado Sam. Es muy amigable y tiene una mancha negra en la espalda.');

  // 4. Seleccionar ubicación manualmente para Buenos Aires, Argentina
  // Si la IA ya abrió el modo manual (porque detectó una ubicación), no hace falta hacer clic en el botón
  const manualButton = page.locator('button', { hasText: 'Ingresar dirección manualmente' });
  if (await manualButton.isVisible()) {
    await manualButton.click();
  }

  // Rellenar calle y altura
  await page.locator('#street').fill('Calle 50');
  await page.locator('#number').fill('800');

  // Abrir desplegable de localidad
  await page.locator('button', { hasText: 'Seleccionar localidad...' }).click();

  // Buscar una localidad de Buenos Aires (ej. La Plata)
  await page.locator('input[placeholder="Buscar localidad..."]').fill('La Plata');

  // Esperar y hacer clic en la sugerencia correspondiente a La Plata
  await page.locator('button:has-text("La Plata")').first().click();

  // Asegurar que provincia tiene seleccionado "Buenos Aires" por defecto
  const stateSelect = page.locator('#state');
  await expect(stateSelect).toHaveValue('Buenos Aires');

  // Confirmar ubicación
  await page.locator('button', { hasText: 'Confirmar ubicación' }).click();

  // Validar banner de ubicación obtenida
  await expect(page.locator('text=Ubicación obtenida')).toBeVisible();
  await expect(page.locator('text=CALLE 50 800, La Plata, Buenos Aires')).toBeVisible();

  // 5. Enviar el formulario exitosamente
  // Hacemos clic en Publicar
  await page.locator('button[type="submit"]', { hasText: 'Publicar' }).click();

  // Esperar redirección al home (URL /) o mensaje de éxito/aprobación
  await page.waitForURL('**/', { timeout: 15000 });
  
  // Validar que volvimos al listado principal de posts
  await expect(page).toHaveURL(/\/$/);
});
