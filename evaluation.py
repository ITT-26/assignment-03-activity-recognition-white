from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from dataset_loader import load_dataset
from feature_extraction import extract_features

# compares different svm kernel functions
# used to evaluate classifier performance

data, labels = load_dataset("data")

X = []

for frame in data:
    X.append(extract_features(frame))

X_train, X_test, y_train, y_test = train_test_split(
    X,
    labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)

kernels = ["linear", "poly", "rbf"]

for kernel in kernels:

    model = make_pipeline(
        StandardScaler(),
        SVC(kernel=kernel)
    )

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)

    print(kernel, acc)