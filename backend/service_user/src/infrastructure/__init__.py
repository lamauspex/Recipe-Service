from .container import container


# serve_grpc импортируется только при явном вызов
def __getattr__(name):
    if name == 'serve_grpc':
        from .grpc_server import serve_grpc
        return serve_grpc
    raise AttributeError(f"module {name!r} not found")


__all__ = ['container', 'serve_grpc']
