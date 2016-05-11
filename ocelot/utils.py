def extract_products_as_tuple(dataset):
    return tuple([exc['name']
                  for exc in dataset['exchanges']
                  if exc['type'] == 'reference product'])
