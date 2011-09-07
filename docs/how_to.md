# Generating graph_models

Assuming you have `dot` installed (graphviz)

	workon regluit; python manage.py graph_models --settings=regluit.settings.me core > docs/core_db_schema.dot
        dot -Tpng docs/core_db_schema.dot > docs/core_db_schema.png
