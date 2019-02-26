from project.docs import bp


@bp.route('/')
@bp.route('/<path:filename>')
def serve_sphinx_docs(filename='index.html'):
    return bp.send_static_file(filename)
