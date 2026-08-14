<?php
$preguntas_seguridad = [
    'primer_amor'          => '¿Cómo se llamaba tu primer amor?',
    'maestro_favorito'     => '¿Quién fue tu maestro(a) favorito(a)?',
    'lugar_nacimiento'     => '¿En qué ciudad o lugar naciste?',
    'pais_visitar'         => '¿Qué país te gustaría visitar?',
    'dia_memorable'        => '¿Cuál es tu día o fecha más memorable?',
    'primera_escuela'      => '¿Cómo se llamaba tu primera escuela?',
    'primera_mascota'      => '¿Cuál es el nombre de tu primera mascota?',
    'comida_favorita'      => '¿Cuál es tu comida favorita?',
    'mejor_amigo_infancia' => '¿Cómo se llamaba tu mejor amigo(a) de la infancia?',
    'primer_trabajo'       => '¿Cuál fue tu primer trabajo?'
];
?>

<?php for ($i = 1; $i <= 3; $i++): ?>
    <label for="pregunta_seguridad_<?= $i ?>">Pregunta de Seguridad <?= $i ?>:</label>
    <select name="pregunta_seguridad_<?= $i ?>" id="pregunta_seguridad_<?= $i ?>" required>
        <option value="" disabled selected>Seleccione una pregunta</option>
        <?php foreach ($preguntas_seguridad as $clave => $texto): ?>
            <option value="<?= $clave ?>"><?= $texto ?></option>
        <?php endforeach; ?>
    </select>
    <br>
    <label for="respuesta_seguridad_<?= $i ?>">Respuesta <?= $i ?>:</label>
    <input type="text" id="respuesta_seguridad_<?= $i ?>" name="respuesta_seguridad_<?= $i ?>" required>
    <br>
<?php endfor; ?>