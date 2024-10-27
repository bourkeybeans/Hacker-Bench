import numpy as np

class Model:
    """Stores vertex information for a 3D Model"""
    def __init__(self, fileName: str, objectNames: list[str] = []) -> None:
        self.vertices = []
        self.edges = set()
        self.objects = []

        if len(objectNames) > 0:
            self.load_model(fileName, objectNames)
        else:
            self.load_model(fileName)


    def load_model(self, fileName: str, objectNames: list[str] = []) -> None:
        """Loads vertices from a .obj file with file name 'fileName'

        :param fileName: The filename of the .obj file to load
        :param objectName: The name of a specific object to load from the specified .obj file"""
        
        self.vertices = []
        self.edges = set()

        try:
            with open(f'Games/OrientationTest/Assets/{fileName}', 'r') as file:
                for line in file:
                    if len(objectNames) > 0:
                        if line.startswith('o ') and (line.split()[1] not in objectNames):
                            break
                    
                    # Extracts object names
                    if line.startswith('o '):
                        self.objects.append(line.split()[1])

                    # Extracts vertex data from line
                    elif line.startswith('v '):
                        parts = line.strip().split()
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        self.vertices.append(np.matrix([x, y, z]))

                    # Extracts edge data face
                    elif line.startswith('f '):
                        parts = line.strip().split()
                        vertex_indices = [int(part.split('/')[0]) for part in parts[1:]]
                        for i in range(len(vertex_indices)):
                            v1 = vertex_indices[i]
                            v2 = vertex_indices[(i + 1) % len(vertex_indices)]  # Wrap around to create a loop
                            edge = tuple(sorted((v1-1, v2-1)))  # Sort to avoid duplicates like (1, 2) and (2, 1)
                            self.edges.add(edge)

        except FileNotFoundError:
            print(f"File not found: {fileName}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    model = Model('Donut.obj', ['Doughnut_Torus.003'])
    print(len(model.edges))