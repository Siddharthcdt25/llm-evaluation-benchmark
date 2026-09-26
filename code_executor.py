def execute_code(code):

    namespace = {}

    try:
        exec(code, namespace)

        return {
            "success": True,
            "namespace": namespace,
            "error": None
        }

    except Exception as e:

        return {
            "success": False,
            "namespace": {},
            "error": str(e)
        }