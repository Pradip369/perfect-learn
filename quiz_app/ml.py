from sklearn import datasets
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pylab as pl
from pandas.plotting import scatter_matrix
import matplotlib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from io import BytesIO
import base64

matplotlib.use('Agg')

def generate_graph(file_obj,target_name):
     dtf= pd.read_csv(file_obj)
     #Visualization
     sns.countplot(dtf[target_name],label="Count")
     buffer = BytesIO()
     plt.savefig(buffer, format='png')
     buffer.seek(0)
     image_png = buffer.getvalue()
     buffer.close()
     bar_chart = base64.b64encode(image_png)
     bar_chart = bar_chart.decode('utf-8')
     plt.close()
     # plt.show()
     
     dtf.drop(target_name, axis=1).plot(kind='box', subplots=True, layout=(3,3), sharex=False, sharey=False, figsize=(10,10),title='Box Plot for each input variable')
     buffer = BytesIO()
     plt.savefig(buffer, format='png')
     buffer.seek(0)
     image_png = buffer.getvalue()
     buffer.close()
     box_chart = base64.b64encode(image_png)
     box_chart = box_chart.decode('utf-8')
     plt.close()
     
     dtf.drop(target_name ,axis=1).hist(bins=30, figsize=(10,10))
     pl.suptitle("Histogram for each numeric input variable")
     buffer = BytesIO()
     plt.savefig(buffer, format='png')
     buffer.seek(0)
     image_png = buffer.getvalue()
     buffer.close()
     histo_chart = base64.b64encode(image_png)
     histo_chart = histo_chart.decode('utf-8')
     plt.close()

     X = dtf.drop(target_name, axis=1)
     y = dtf[target_name]

     cmap = matplotlib.cm.get_cmap('gnuplot')
     scatter = pd.plotting.scatter_matrix(X, c = y, marker = 'o', s=40, hist_kwds={'bins':15}, figsize=(7,7), cmap = cmap)
     plt.suptitle('Scatter-matrix for each input variable')
     buffer = BytesIO()
     plt.savefig(buffer, format='png')
     buffer.seek(0)
     image_png = buffer.getvalue()
     buffer.close()
     scat_chart = base64.b64encode(image_png)
     scat_chart = scat_chart.decode('utf-8')
     plt.close()

     # #Create Training and Test Sets and Apply Scaling
     X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.3,random_state=0)
     scaler = MinMaxScaler()
     X_train = scaler.fit_transform(X_train)
     X_test = scaler.transform(X_test)

     # #Build Models
     # #Logistic Regression
     logreg = LogisticRegression()
     logreg.fit(X_train, y_train)
     logi_tr = '{:.2f}'.format(logreg.score(X_train, y_train))
     logi_test = '{:.2f}'.format(logreg.score(X_test, y_test))
     
     # print('Accuracy of Logistic regression classifier on training set: {:.2f}'
     #      .format(logreg.score(X_train, y_train)))
     # print('Accuracy of Logistic regression classifier on test set: {:.2f}'
     #      .format(logreg.score(X_test, y_test)))


     # #Decision Tree
     clf = DecisionTreeClassifier().fit(X_train, y_train)
     dec_tr = '{:.2f}'.format(clf.score(X_train, y_train))
     dec_test = '{:.2f}'.format(clf.score(X_test, y_test))
     
     # print('Accuracy of Decision Tree classifier on training set: {:.2f}'
     #      .format(clf.score(X_train, y_train)))
     # print('Accuracy of Decision Tree classifier on test set: {:.2f}'
     #      .format(clf.score(X_test, y_test)))

     # #K-Nearest Neighbors
     knn = KNeighborsClassifier()
     knn.fit(X_train, y_train)
     # knn_tr = 0
     # knn_test = 0
     try:
          knn_tr = '{:.2f}'.format(knn.score(X_train, y_train))
          knn_test = '{:.2f}'.format(knn.score(X_test, y_test))
     except Exception:
          knn_tr = "No more data"
          knn_test = "No more data"
     
     # print('Accuracy of K-NN classifier on training set: {:.2f}'
     #      .format(knn.score(X_train, y_train)))
     # print('Accuracy of K-NN classifier on test set: {:.2f}'
     #      .format(knn.score(X_test, y_test)))
     
     #Linear Discriminant Analysis
     from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
     lda = LinearDiscriminantAnalysis()
     try:
          lda.fit(X_train, y_train)
          lda_tr = lda.score(X_train, y_train)
          lda_test = lda.score(X_test, y_test)
     except:
          lda_tr = "No More Data"
          lda_test = "No More Data"
     # print('Accuracy of LDA classifier on training set: {:.2f}'
     #      .format(lda.score(X_train, y_train)))
     # print('Accuracy of LDA classifier on test set: {:.2f}'
     #      .format(lda.score(X_test, y_test)))

     #Gaussian Naive Bayes
     from sklearn.naive_bayes import GaussianNB
     gnb = GaussianNB()
     gnb.fit(X_train, y_train)
     gnb_tr = gnb.score(X_train, y_train)
     gnb_test = gnb.score(X_test, y_test)
     
     # print('Accuracy of GNB classifier on training set: {:.2f}'
     #      .format(gnb.score(X_train, y_train)))
     # print('Accuracy of GNB classifier on test set: {:.2f}'
     #      .format(gnb.score(X_test, y_test)))

     #Support Vector Machine
     from sklearn.svm import SVC
     svm = SVC()
     svm.fit(X_train, y_train)
     svm_tr = svm.score(X_train, y_train)
     svm_test = svm.score(X_test, y_test)
     
     # print('Accuracy of SVM classifier on training set: {:.2f}'
     #      .format(svm.score(X_train, y_train)))
     # print('Accuracy of SVM classifier on test set: {:.2f}'
     #      .format(svm.score(X_test, y_test)))

     # pred = clf.predict(X_test)
     # dec_predict = pred
     # _confusion_matrix = confusion_matrix(y_test, pred)
     # _classification_report = classification_report(y_test, pred)
     # print(pred)
     # print(confusion_matrix(y_test, pred))
     # print(classification_report(y_test, pred))

     data_dict = {
          "target_name" : target_name,
          'logi_tr' : logi_tr,
          'logi_test' : logi_test,
          'dec_tr' : dec_tr,
          'dec_test' : dec_test,
          'knn_tr' : knn_tr,
          'knn_test' : knn_test,

          'lda_tr' : lda_tr,
          'lda_test' : lda_test,
          'gnb_tr' : gnb_tr,
          'gnb_test' : gnb_test,
          'svm_tr' : svm_tr,
          'svm_test' : svm_test,

          'bar_chart' : bar_chart,
          'box_chart' : box_chart,
          'histo_chart' : histo_chart,
          'scat_chart' : scat_chart
     }
     return data_dict