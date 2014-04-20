/*global module:false*/
module.exports = function(grunt) {
    "use strict";

    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-symlink');

    var pkg = grunt.file.readJSON(__filename.split('/').slice(0, -1).concat(['package.json']).join('/')),
        dest_static = 'dist/static/',
        dest_tpl = 'dist/templates/';

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
                dest: dest_static + 'yati/js/yati.js'
            }
        },
        symlink: {
            ext: {
                expand: true,
                cwd: 'ext',
                src: ['*'],
                dest: dest_static + 'yati/js/'
            },
            tpl: {
                expand: true,
                cwd: 'tpl',
                src: ['*'],
                dest: dest_tpl
            },
            devel: {
                expand: true,
                cwd: 'src',
                src: ['*'],
                dest: dest_static + 'yati/js/'
            },
            css: {
                expand: true,
                cwd: 'css',
                src: ['*'],
                dest: dest_static + 'yati/css/'
            },
            img: {
                expand: true,
                cwd: 'img',
                src: ['*'],
                dest: dest_static + 'yati/img/'
            }
        },
        clean: [dest_static+'*', dest_tpl + '*']
    });

    grunt.registerTask('build', ['clean', 'concat:yati', 'symlink:ext', 'symlink:tpl', 'symlink:devel', 'symlink:css', 'symlink:img']);
    grunt.registerTask('default', ['build']);

};
