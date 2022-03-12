from importlib.util import module_for_loader
from tokenize import group
import numpy as np
from sklearn.cluster import DBSCAN
from PIL import Image
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#%matplotlib inline
import geojson as gj
from operator import itemgetter
from scipy.spatial import distance


def preprocess_img(fimg_name):
    img = Image.open(fimg_name)
    img_data = np.asarray(img)
    data = []
    for x in range(img.width):
        for y in range(img.height):
            z = int(3 * img_data[x][y][2] + 2 * img_data[x][y][1] + img_data[x][y][0])
            data.append((x, y, z))
    return data


def clusterize(data):
    model = DBSCAN(eps=2.5, min_samples=2, algorithm='ball_tree', n_jobs=4)
    model.fit_predict(data)
    pred = model.fit_predict(data)
    print(f'# clusters: {len(set(model.labels_))}')
    print(f'labels {model.labels_}')
    # to_rem = []
    # for idx, l in enumerate(model.labels_):
    #     if l == -1:
    #         to_rem.append(idx)
    # for r_idx in to_rem:
    #     del model.labels_[r_idx]
    #     del data[r_idx]
    return model.labels_


def draw_clusters(clusters, centroids=None):
    coords = np.array([list(t) for t in clusters.keys()])
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(coords.T[0], coords.T[1], coords.T[2], c=list(float(f) for f in clusters.values()), s=30)
    if centroids:
        for cluster_id in set(clusters.values()):
            centroid = centroids[cluster_id]
            ax.scatter(centroid[0], centroids[1], centroids[2], c=[100, 100, 100], s=50)
    ax.view_init(azim=200)
    plt.show()


'''
Given a set of clusters of the form  { cluter_id : [ (x, y), .. ] }
calculates the centroids of the clusters
'''
def estimate_centroids(clusters):
    clusters_with_centroids = {}
    for cluster_id, coords3d in clusters.items():
        # coords2d = [(x, y, z) for x,y,z in coords3d]
        clusters_with_centroids[cluster_id] = tuple(np.mean(coords3d, axis=0))
        # print(clusters_with_centroids[cluster_id])
    return clusters_with_centroids


'''
Accepts clusters = { cluster_id : [ (x, y, z), (x1, y1, z1), ... ] }
Produces { cluter_id : [ (x, y), .. ] } where (x,y) are euclidean coords
'''
def group_clusters(clusters):
    grouped = {}
    for coords, cluster_id in clusters.items():
        if cluster_id not in grouped:
            grouped[cluster_id] = [coords]
        else:
            grouped[cluster_id].append(coords)
    return grouped


'''
Accepts clusters = { cluster_id : [ (x, y, z), (x1, y1, z1), ... ] }
Creates a map containing the probability for each position of the cluster to be
appropriate for landing.
Returns [ a1, a2, a3, a4, ...] where aN е [0; 1]
'''
def make_probab_map(grouped_clusters, centroids):
    probab_map = {}
    for cluster_id in grouped_clusters.keys():
        cluster_centroid = centroids[cluster_id]
        total_coords3d = group_clusters[cluster_id]
        for coords in total_coords3d:
            dist = distance.euclidean(cluster_centroid, coords)
            probab_map[tuple(coords)] = dist
    max_dist = max(probab_map.values())
    if max_dist == 0:
        max_dist = 1
    for k, _ in probab_map.items():
        probab_map[k] /= max_dist


'''
Accepts clusters of the form { cluster_id : [ (x, y, z), (x1, y1, z1), ... ] }
Selects points which should be passed back to gatewat for rendering.
'''
def geoborders(grouped_clusters, probab_map):
    N = 10
    for cluster_id, coords3d in grouped_clusters:
        res = dict(sorted(probab_map.items(), key = itemgetter(1), reverse = False)[:N])


def main():
    data = preprocess_img('31.jpg')
    clusters = clusterize(data)
    grouped_clusters = group_clusters(clusters)
    centroids = estimate_centroids(grouped_clusters)
    draw_clusters(clusters, None)
    # probab_map = make_probab_map(group_clusters, clusters)
    # print(probab_map)
    # coords = translate_map()


if __name__ == "__main__":
    main()
