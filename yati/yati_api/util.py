import os

from django.conf import settings

from yati_api.models import Project, Store, Unit

LANG_CODES = map(lambda l: l[0], settings.LANGUAGES)

def add_stores_from_django_locale(path, project_name=None, project=None, po_name='django', dry_run=False, sourcelanguage='en'):
    """
    Shortcut for adding stores (and making a project) from django's locale/ directory

    path            path to your project's locale/ directory
    project         add stores to existing project
    project_name    name of resulting project
    po_name         name of pofiles to store (only one per project/language combination)
                    po_name.po file is taken (so default 'django' or 'djangojs' should usually do it)
    sourcelanguage  source language
    dry_run         if true no database records will be created/modified, list of store dicts will be returned
    """

    if not project_name: project_name = po_name
    if not project and not dry_run:
        assert not Project.objects.filter(name=project_name).exists()

    stores = []
    for d in os.listdir(path):
        if d in LANG_CODES:
            fn = os.path.join(path, d, 'LC_MESSAGES', '%s.po'%po_name)    # @TODO lc_messages?
            if os.path.exists(fn):
                stores.append(dict(filename=fn, targetlanguage=d, sourcelanguage=sourcelanguage, type='po'))

    if dry_run: return stores

    # make records
    if not project:
        project = Project.objects.create(name=project_name or po_name)
    for store in stores:
        s = project.stores.create(**store)
        s.update(s.filename)

    return project

def update_project(project, dry_run):
    """
    Takes projects' stores and tries to update them from store.filename (if exists)
    Watch out, do dry_run before anything weird happens
    """
    print 'Updating project %s%s'%(project, ' DRY RUN' if dry_run else '')
    for store in project.stores.all():
        if os.path.exists(store.filename):
            print 'For %s found file %s'%(store, store.filename)
            if not dry_run:
                store.update(store.read(store.filename))
        else:
            print 'For %s NO FILE FOUND %s'%(store, store.filename)

def export_project(project, dry_run):
    """
    Takes projects' stores and tries to export them to store.filename
    Watch out, do dry_run before anything weird happens
    """
    print 'Exporting project %s%s'%(project, ' DRY RUN' if dry_run else '')
    for store in project.stores.all():
        if not store.filename:
            print '%s has no filename set, ignoring'%store
        else:
            print 'Exporting %s to file %s'%(store, store.filename)
            if not dry_run:
                store.write(store.filename)

def europarl_make_pofile(sourcefn, targetfn, limit=None):
    """
    Make a pofile (pypo.pofile instance) out of two europarl text files
    """

    from translate.storage import pypo

    source = open(sourcefn, 'r')
    target = open(targetfn, 'r')
    pofile = pypo.pofile()

    i = 0
    while True:
        sline = source.readline()
        tline = target.readline()

        # EOF, break
        if sline == '': break
        sline = sline.strip()   
        tline = tline.strip()

        # empty line, continue
        if not sline or not tline: continue

        pounit = pypo.pounit(source=sline)
        pounit.target = tline
        pofile.addunit(pounit)

        # limit reached, break
        i += 1
        if limit and i >= limit: break

    source.close()
    target.close()

    return pofile

def pofile_to_terminology(pofile):
    from translate.tools import poterminology

    tex = poterminology.TerminologyExtractor()
    tex.processunits(pofile.units, 'FILE')

    items = []
    for item in tex.extract_terms().values(): #sorted(tex.extract_terms().values(), key=lambda t: t[0], reverse=True)
        source = Unit.pounit_get(item[1], 'source')
        strings = filter(lambda s: bool(s), map(unicode.strip, Store.RE_CLEARTERM.sub('', unicode(item[1].gettarget())).split(';')))
        if len(strings):
            items.append((source, strings))

    return items
