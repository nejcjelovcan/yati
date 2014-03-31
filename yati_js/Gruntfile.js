/*global module:false*/
module.exports = function(grunt) {
    "use strict";

    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-copy');

    var pkg = grunt.file.readJSON(__filename.split('/').slice(0, -1).concat(['package.json']).join('/')),
        dest = '../yati/yati_api/';

    // Project configuration.
    grunt.initConfig({
        pkg: pkg,
        concat: {
            yati: {
                src: [
                    'src/core.js',
                    'src/models.js',
                    'src/views.js',
                    'src/app.js'
                ],
                dest: dest + 'static/yati/js/yati.js'
            }
        },
        copy: {
            ext: {
                expand: true,
                flatten: true,
                src: 'ext/*',
                dest: dest + 'static/yati/js/'
            },
            tpl: {
                src: 'tpl/*',
                dest: dest + 'templates/'
            },
            devel: {
                expand: true,
                flatten: true,
                src: 'src/*',
                dest: dest + 'static/yati/js/'
            }
        }/*,
        clean: [dest+'static/yati/js/*.js', dest+'templates/tpl/*.tpl']*/
    });

    grunt.registerTask('build', ['concat:yati', 'copy:ext', 'copy:tpl', 'copy:devel']);
    grunt.registerTask('default', ['build']);

};
