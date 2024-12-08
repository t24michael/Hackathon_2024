import os

import torch
from PIL import Image
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models


class Xra:
    def __init__(self, img_path = "images"):
        self.img_path = img_path
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
        self.img_files = os.listdir(self.img_path)

    def __len__(self):
        return len(self.img_files)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_path, self.img_files[idx]).replace("\\", "/")

        if "normal" in self.img_files[idx].lower():
            label = 0
        elif "covid" in self.img_files[idx].lower():
            label = 1
        elif "lung_opacity" in self.img_files[idx].lower():
            label = 2
        elif "viral pneumonia" in self.img_files[idx].lower():
            label = 3
        else:
            label = -1
            raise ValueError(f"Unknown category in file: {self.img_files[idx]}")

        img = Image.open(img_path).convert("RGB")
        if self.transform:
            img = self.transform(img)

        return img, label

    def init(self):
        self.dataloader = DataLoader(self, batch_size=1, shuffle=True)

        self.model = models.resnet18(pretrained=True)
        self.model.fc = nn.Linear(self.model.fc.in_features, 4)

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0001)

        self.device = torch.device("cpu")
        self.model.to(self.device)

    def train(self, epochs = 5):
        for epoch in range(epochs):
            self.model.train()
            running_loss = 0.0
            print(f"Entering epoch: {epoch + 1}")

            for images, labels in self.dataloader:
                images, labels = images.to(self.device), labels.to(self.device)

                outputs = self.model(images)
                loss = self.criterion(outputs, labels)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                running_loss += loss.item()

            print(f"Epoch {epoch + 1}/{epochs}, Loss: {running_loss / len(self.dataloader)}")
            torch.save(self.model.state_dict(), "model.pth")

        print("Training complete.")

    def evaluate(self, img_path):
        self.model.load_state_dict(torch.load("modeL.pth"))
        self.model.eval()

        image = Image.open(img_path).convert("RGB")
        image_tensor = self.transform(image).to(self.device)
        image_tensor = image_tensor.unsqueeze(0)
        with torch.no_grad():
            output = self.model(image_tensor)

        class_labels = ["Normal", "COVID", "Lung Opacity", "Viral Pneumonia"]
        _, predicted_class = torch.max(output, 1)
        pred_label = class_labels[predicted_class.item()]

        print(f"{pred_label}")
        return pred_label